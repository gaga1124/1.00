from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import AwardType, AwardApplication, AwardPublicity
from .serializers import (
    AwardTypeSerializer, AwardApplicationSerializer, AwardPublicitySerializer
)


class AwardTypeViewSet(viewsets.ModelViewSet):
    """奖项类型视图集"""
    queryset = AwardType.objects.filter(is_active=True)
    serializer_class = AwardTypeSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """获取可申请的奖项"""
        now = timezone.now()
        awards = self.queryset.filter(
            Q(application_start__lte=now) | Q(application_start__isnull=True),
            Q(application_end__gte=now) | Q(application_end__isnull=True)
        )
        serializer = self.get_serializer(awards, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def match(self, request, pk=None):
        """匹配当前奖项的申请资格"""
        award_type = self.get_object()
        user = request.user
        if not hasattr(user, 'student_profile'):
            return Response({'error': '只有学生可以匹配申请资格'}, status=status.HTTP_400_BAD_REQUEST)
        
        from .utils import match_award_conditions
        result = match_award_conditions(user.student_profile, award_type)
        return Response(result)


class AwardApplicationViewSet(viewsets.ModelViewSet):
    """评奖评优申请视图集"""
    queryset = AwardApplication.objects.all()
    serializer_class = AwardApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据用户角色过滤"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        # 学生只能看自己的
        if hasattr(user, 'student_profile'):
            return queryset.filter(student=user.student_profile)
        
        # 管理员可以看所有
        if user.is_staff:
            return queryset
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """创建申请时自动匹配条件"""
        application = serializer.save(student=self.request.user.student_profile)
        
        # 自动匹配评选条件
        match_result = self._match_criteria(application)
        application.match_score = match_result['score']
        application.match_details = match_result['details']
        application.save()
    
    def _match_criteria(self, application):
        """匹配评选条件"""
        from .utils import match_award_conditions
        result = match_award_conditions(application.student, application.award_type)
        return {'score': result['score'], 'details': result['details']}
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """提交申请"""
        application = self.get_object()
        if application.status != 'draft':
            return Response({'error': '只能提交草稿状态的申请'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'submitted'
        application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """审核申请"""
        application = self.get_object()
        action_type = request.data.get('action')  # 'approve' or 'reject'
        comment = request.data.get('comment', '')
        
        if action_type == 'approve':
            application.status = 'approved'
        elif action_type == 'reject':
            application.status = 'rejected'
        else:
            return Response({'error': '无效的操作'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.reviewer = request.user
        application.review_comment = comment
        application.review_time = timezone.now()
        application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publicize(self, request, pk=None):
        """公示"""
        application = self.get_object()
        if application.status != 'approved':
            return Response({'error': '只能公示已通过的申请'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'publicized'
        application.publicize_start = timezone.now()
        application.publicize_end = timezone.now() + timezone.timedelta(days=7)  # 公示7天
        application.save()
        
        # 创建公示记录
        AwardPublicity.objects.create(
            application=application,
            title=f"{application.award_type.name}公示",
            content=f"经审核，{application.student.user.real_name}同学符合{application.award_type.name}评选条件，现予以公示。",
            start_time=application.publicize_start,
            end_time=application.publicize_end
        )
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)


class AwardPublicityViewSet(viewsets.ReadOnlyModelViewSet):
    """公示记录视图集（只读）"""
    queryset = AwardPublicity.objects.filter(is_active=True)
    serializer_class = AwardPublicitySerializer
    permission_classes = [IsAuthenticated]
