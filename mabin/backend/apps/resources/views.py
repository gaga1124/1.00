from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import ResourceCategory, Resource, ResourceBooking
from .serializers import (
    ResourceCategorySerializer, ResourceSerializer, ResourceBookingSerializer
)


class ResourceCategoryViewSet(viewsets.ModelViewSet):
    """资源分类视图集"""
    queryset = ResourceCategory.objects.filter(is_active=True)
    serializer_class = ResourceCategorySerializer
    permission_classes = [IsAuthenticated]


class ResourceViewSet(viewsets.ModelViewSet):
    """资源视图集"""
    queryset = Resource.objects.filter(is_active=True)
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'category', 'department', 'is_active']
    search_fields = ['name', 'location', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name', 'capacity']
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """检查资源在指定时间段的可用性"""
        resource = self.get_object()
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        
        if not start_time or not end_time:
            return Response({'error': '必须提供开始时间和结束时间'}, status=400)
        
        # 检查是否有冲突的预约
        conflicts = ResourceBooking.objects.filter(
            resource=resource,
            status__in=['pending', 'approved'],
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        is_available = not conflicts.exists()
        
        return Response({
            'is_available': is_available,
            'conflicts': ResourceBookingSerializer(conflicts, many=True).data if conflicts.exists() else []
        })
    
    @action(detail=True, methods=['get'])
    def calendar(self, request, pk=None):
        """获取资源日历视图数据"""
        resource = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        bookings = ResourceBooking.objects.filter(
            resource=resource,
            status__in=['pending', 'approved']
        )
        
        if start_date:
            bookings = bookings.filter(start_time__gte=start_date)
        if end_date:
            bookings = bookings.filter(end_time__lte=end_date)
        
        serializer = ResourceBookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近新增的资源列表
        
        支持查询参数：
        - limit: 返回条数，默认 8
        - resource_type: 资源类型过滤
        - category: 分类ID过滤
        """
        limit = request.query_params.get('limit')
        try:
            limit = int(limit) if limit else 8
        except ValueError:
            limit = 8
        
        qs = self.get_queryset().order_by('-created_at')
        resource_type = request.query_params.get('resource_type')
        category = request.query_params.get('category')
        if resource_type:
            qs = qs.filter(resource_type=resource_type)
        if category:
            qs = qs.filter(category_id=category)
        
        qs = qs[:max(1, min(limit, 50))]  # 最多返回 50 条，至少 1 条
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ResourceBookingViewSet(viewsets.ModelViewSet):
    """资源预约视图集"""
    queryset = ResourceBooking.objects.all()
    serializer_class = ResourceBookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据用户角色过滤"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser or getattr(user, 'has_role', None) and user.has_role('resource_admin'):
            return queryset
        
        return queryset.filter(
            Q(applicant=user) |
            Q(resource__approver=user, status='pending')
        ).distinct()
    
    def perform_create(self, serializer):
        """创建预约时自动设置申请人"""
        booking = serializer.save(applicant=self.request.user)
        
        # 检查时间冲突
        conflicts = ResourceBooking.objects.filter(
            resource=booking.resource,
            status__in=['pending', 'approved'],
            start_time__lt=booking.end_time,
            end_time__gt=booking.start_time
        ).exclude(id=booking.id)
        
        if conflicts.exists():
            # 如果资源需要审批，仍然创建但标记为待审批
            if booking.resource.require_approval:
                booking.status = 'pending'
                booking.save()
            else:
                # 如果不需要审批但有冲突，删除刚创建的记录并抛出异常
                booking.delete()
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'error': '该时间段已被预约',
                    'conflicts': ResourceBookingSerializer(conflicts, many=True).data
                })
        else:
            # 如果不需要审批且无冲突，自动批准
            if not booking.resource.require_approval:
                booking.status = 'approved'
                booking.save()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批预约"""
        booking = self.get_object()
        action_type = request.data.get('action')  # 'approve' or 'reject'
        comment = request.data.get('comment', '')
        
        if booking.resource.approver != request.user and not request.user.is_superuser and not (getattr(request.user, 'has_role', None) and request.user.has_role('resource_admin')):
            return Response({'error': '无权审批此预约'}, status=403)
        
        if action_type == 'approve':
            # 再次检查冲突
            conflicts = ResourceBooking.objects.filter(
                resource=booking.resource,
                status__in=['pending', 'approved'],
                start_time__lt=booking.end_time,
                end_time__gt=booking.start_time
            ).exclude(id=booking.id)
            
            if conflicts.exists():
                return Response(
                    {'error': '该时间段已被预约', 'conflicts': ResourceBookingSerializer(conflicts, many=True).data},
                    status=400
                )
            
            booking.status = 'approved'
            booking.approval_time = timezone.now()
        elif action_type == 'reject':
            booking.status = 'rejected'
        else:
            return Response({'error': '无效的操作类型'}, status=400)
        
        booking.approver = request.user
        booking.approval_comment = comment
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消预约"""
        booking = self.get_object()
        
        # 只有申请人可以取消
        if booking.applicant != request.user and not request.user.is_superuser:
            return Response({'error': '无权取消此预约'}, status=403)
        
        if booking.status in ['completed', 'cancelled']:
            return Response({'error': '该预约已无法取消'}, status=400)
        
        booking.status = 'cancelled'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
