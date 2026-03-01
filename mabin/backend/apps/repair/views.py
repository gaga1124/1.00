from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q, Count
from .models import RepairCategory, RepairApplication, RepairRecord
from .serializers import (
    RepairCategorySerializer, RepairApplicationSerializer, RepairRecordSerializer
)


class RepairCategoryViewSet(viewsets.ModelViewSet):
    """报修分类视图集"""
    queryset = RepairCategory.objects.filter(is_active=True)
    serializer_class = RepairCategorySerializer
    permission_classes = [IsAuthenticated]


class RepairApplicationViewSet(viewsets.ModelViewSet):
    """报修申请视图集"""
    queryset = RepairApplication.objects.all()
    serializer_class = RepairApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def _is_logistics(self, user):
        """是否为后勤处人员（通过角色判断）"""
        try:
            return bool(getattr(user, 'has_role', None) and user.has_role('logistics'))
        except Exception:
            return False
    
    def get_queryset(self):
        """根据用户角色过滤"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # 超级管理员、管理员、后勤处可以看到所有
        if user.is_superuser or user.is_staff or self._is_logistics(user):
            return queryset
        
        # 辅导员可查看自己管理学生的报修 + 处理人 + 自己申请的
        counselor_repairs = queryset.filter(applicant__student_profile__counselor=user)
        handler_repairs = queryset.filter(handler=user)
        applicant_repairs = queryset.filter(applicant=user)
        return (counselor_repairs | handler_repairs | applicant_repairs).distinct()
    
    def perform_create(self, serializer):
        """创建申请仅允许学生，自动设置申请人"""
        user = self.request.user
        if not getattr(user, 'is_student_user', False):
            raise PermissionDenied('只有学生可以发起报修申请')
        serializer.save(applicant=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取报修统计"""
        user = request.user
        
        # 我的报修统计
        my_repairs = RepairApplication.objects.filter(applicant=user)
        my_stats = {
            'total': my_repairs.count(),
            'pending': my_repairs.filter(status='pending').count(),
            'processing': my_repairs.filter(status='processing').count(),
            'completed': my_repairs.filter(status='completed').count(),
        }
        
        # 待处理统计（管理员/后勤处）
        if user.is_superuser or user.is_staff or self._is_logistics(user):
            pending_count = RepairApplication.objects.filter(status='pending').count()
            my_stats['pending_handling'] = pending_count
        
        return Response(my_stats)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """受理报修"""
        application = self.get_object()
        user = request.user
        
        # 权限：管理员/超级管理员/后勤处人员 才能受理
        if not (user.is_superuser or user.is_staff or self._is_logistics(user)):
            raise PermissionDenied('无权受理报修')
        
        if application.status != 'pending':
            return Response({'error': '该报修已受理或已处理'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'accepted'
        application.handler = request.user
        application.accepted_at = timezone.now()
        application.save()
        
        # 创建处理记录
        RepairRecord.objects.create(
            application=application,
            operator=request.user,
            action='受理',
            comment=request.data.get('comment', '')
        )
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start_processing(self, request, pk=None):
        """开始处理"""
        application = self.get_object()
        user = request.user
        
        # 权限：管理员/超级管理员/后勤处人员 才能处理
        if not (user.is_superuser or user.is_staff or self._is_logistics(user)):
            raise PermissionDenied('无权处理报修')
        
        if application.status not in ['accepted', 'pending']:
            return Response({'error': '该报修状态不允许此操作'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'processing'
        application.handler = request.user
        if not application.accepted_at:
            application.accepted_at = timezone.now()
        application.save()
        
        RepairRecord.objects.create(
            application=application,
            operator=request.user,
            action='开始处理',
            comment=request.data.get('comment', '')
        )
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成报修"""
        application = self.get_object()
        user = request.user
        
        # 权限：管理员/超级管理员/后勤处人员 才能完成
        if not (user.is_superuser or user.is_staff or self._is_logistics(user)):
            raise PermissionDenied('无权完成报修')
        
        if application.status != 'processing':
            return Response({'error': '该报修未在处理中'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'completed'
        application.completed_at = timezone.now()
        application.handler_comment = request.data.get('comment', '')
        application.save()
        
        RepairRecord.objects.create(
            application=application,
            operator=request.user,
            action='完成',
            comment=request.data.get('comment', ''),
            images=request.data.get('images', [])
        )
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """评价报修"""
        application = self.get_object()
        
        if application.applicant != request.user:
            return Response({'error': '只能评价自己的报修'}, status=status.HTTP_403_FORBIDDEN)
        
        if application.status != 'completed':
            return Response({'error': '只能评价已完成的报修'}, status=status.HTTP_400_BAD_REQUEST)
        
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return Response({'error': '评分必须在1-5之间'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.rating = rating
        application.applicant_comment = comment
        application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消报修"""
        application = self.get_object()
        
        if application.applicant != request.user:
            return Response({'error': '只能取消自己的报修'}, status=status.HTTP_403_FORBIDDEN)
        
        if application.status in ['completed', 'cancelled']:
            return Response({'error': '该报修无法取消'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'cancelled'
        application.save()
        
        RepairRecord.objects.create(
            application=application,
            operator=request.user,
            action='取消',
            comment=request.data.get('comment', '')
        )
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)


class RepairRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """报修处理记录视图集（只读）"""
    queryset = RepairRecord.objects.all()
    serializer_class = RepairRecordSerializer
    permission_classes = [IsAuthenticated]
