"""
电子签章模块视图
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.http import FileResponse
from django.utils import timezone
from .models import ElectronicFile, DepartmentSignature, FileRecipient, SignatureOperationLog
from .serializers import (
    ElectronicFileListSerializer, ElectronicFileDetailSerializer, ElectronicFileCreateSerializer,
    DepartmentSignatureSerializer, SignFileSerializer, SendFileSerializer, VerifyFileSerializer,
    SignatureOperationLogSerializer
)


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_operation(request, operation, file=None, details=None):
    """记录操作日志"""
    user = request.user
    department = user.department.first() if user.department.exists() else None
    
    if not department:
        return
    
    SignatureOperationLog.objects.create(
        operation=operation,
        file=file,
        user=user,
        department=department,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details=details or {}
    )


class DepartmentSignatureViewSet(viewsets.ModelViewSet):
    """部门签章视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentSignatureSerializer
    
    def get_queryset(self):
        # 只返回当前用户所在部门的签章
        user = self.request.user
        if hasattr(user, 'department') and user.department:
            user_departments = user.department.all()
            return DepartmentSignature.objects.filter(department__in=user_departments)
        # 如果用户没有部门，返回所有启用的签章
        return DepartmentSignature.objects.filter(is_active=True)
    
    def create(self, request, *args, **kwargs):
        """创建部门签章"""
        user = request.user
        department_id = request.data.get('department_id')
        
        # 检查用户是否是部门管理员
        from apps.rbac.models import UserDepartment
        user_dept = UserDepartment.objects.filter(
            user=user,
            department_id=department_id,
            is_admin=True
        ).first()
        
        if not user_dept:
            return Response(
                {'error': '只有部门管理员可以上传签章'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            log_operation(
                request, 
                'upload', 
                details={'signature_id': response.data.get('id')}
            )
        return response


class ElectronicFileViewSet(viewsets.ModelViewSet):
    """电子文件视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'file_name']
    ordering_fields = ['created_at', 'signed_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        # 获取用户所在部门的文件 + 发送给用户的文件
        if hasattr(user, 'department') and user.department:
            user_departments = user.department.all()
            queryset = ElectronicFile.objects.filter(
                Q(department__in=user_departments) | 
                Q(recipients__recipient=user)
            ).distinct()
        else:
            # 如果用户没有部门，只返回发送给用户的文件
            queryset = ElectronicFile.objects.filter(recipients__recipient=user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ElectronicFileListSerializer
        elif self.action == 'create':
            return ElectronicFileCreateSerializer
        return ElectronicFileDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """上传电子文件"""
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            file_id = response.data.get('id')
            file = ElectronicFile.objects.get(id=file_id)
            log_operation(
                request, 
                'upload', 
                file=file,
                details={'file_name': file.file_name}
            )
        return response
    
    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """文件签章"""
        file = self.get_object()
        user = request.user
        
        # 检查权限：只有文件所属部门的人员可以签章
        if user not in file.department.user_set.all():
            return Response(
                {'error': '无权为此文件签章'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 检查文件状态
        if file.status != 'draft':
            return Response(
                {'error': '只能为草稿状态的文件签章'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SignFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signature_id = serializer.validated_data['signature_id']
        
        # 检查签章是否存在且属于同一部门
        signature = DepartmentSignature.objects.filter(
            id=signature_id,
            department=file.department,
            is_active=True
        ).first()
        
        if not signature:
            return Response(
                {'error': '签章不存在或无效'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 执行签章
        file.sign(signature, user)
        
        # 记录日志
        log_operation(
            request, 
            'sign', 
            file=file,
            details={'signature_id': signature_id}
        )
        
        serializer = ElectronicFileDetailSerializer(file, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """发送文件"""
        file = self.get_object()
        user = request.user
        
        # 检查权限
        if user not in file.department.user_set.all():
            return Response(
                {'error': '无权发送此文件'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 检查文件状态
        if file.status != 'signed':
            return Response(
                {'error': '只能发送已签章的文件'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SendFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        recipient_ids = serializer.validated_data.get('recipient_ids', [])
        send_all = serializer.validated_data.get('send_all', False)
        department_ids = serializer.validated_data.get('departments', [])
        
        # 构建接收人列表
        from django.contrib.auth import get_user_model
        User = get_user_model()
        recipients = []
        
        if send_all:
            # 发送给所有人
            recipients = User.objects.filter(is_active=True)
        elif department_ids:
            # 发送给指定部门
            from apps.rbac.models import Department
            departments = Department.objects.filter(id__in=department_ids)
            for dept in departments:
                recipients.extend(dept.user_set.filter(is_active=True))
        elif recipient_ids:
            # 发送给指定用户
            recipients = User.objects.filter(id__in=recipient_ids, is_active=True)
        
        # 去重
        recipient_ids = list(set([r.id for r in recipients]))
        recipients = User.objects.filter(id__in=recipient_ids)
        
        if not recipients:
            return Response(
                {'error': '请至少选择一个接收人'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建接收记录
        for recipient in recipients:
            FileRecipient.objects.get_or_create(
                file=file,
                recipient=recipient
            )
        
        # 更新文件状态
        file.status = 'sent'
        file.save()
        
        # 记录日志
        log_operation(
            request, 
            'send', 
            file=file,
            details={
                'recipient_count': len(recipients),
                'send_all': send_all,
                'departments': department_ids
            }
        )
        
        serializer = ElectronicFileDetailSerializer(file, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """撤回文件"""
        file = self.get_object()
        user = request.user
        
        # 检查权限
        if user not in file.department.user_set.all():
            return Response(
                {'error': '无权撤回此文件'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 检查文件状态
        if file.status != 'sent':
            return Response(
                {'error': '只能撤回已发送的文件'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查撤回时间限制（24小时内可撤回）
        if file.updated_at:
            time_diff = timezone.now() - file.updated_at
            if time_diff.total_seconds() > 24 * 3600:
                return Response(
                    {'error': '文件发送超过24小时，无法撤回'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 执行撤回
        file.status = 'revoked'
        file.save()
        
        # 记录日志
        log_operation(
            request, 
            'revoke', 
            file=file
        )
        
        serializer = ElectronicFileDetailSerializer(file, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """验证文件签章"""
        file = self.get_object()
        
        # 执行验签
        is_valid, message = file.verify_signature()
        
        # 记录验签日志
        log_operation(
            request, 
            'verify', 
            file=file,
            details={'is_valid': is_valid, 'message': message}
        )
        
        return Response({
            'file_id': file.id,
            'file_name': file.file_name,
            'is_valid': is_valid,
            'message': message,
            'department': file.department.name if file.department else None,
            'signed_at': file.signed_at,
            'signer': file.signer.real_name if file.signer else None
        })
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """下载文件"""
        file = self.get_object()
        user = request.user
        
        # 检查权限：文件所属部门人员或接收人可以下载
        has_permission = (
            user in file.department.user_set.all() or
            file.recipients.filter(recipient=user).exists()
        )
        
        if not has_permission:
            return Response(
                {'error': '无权下载此文件'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 标记为已读
        recipient = file.recipients.filter(recipient=user).first()
        if recipient:
            recipient.mark_as_read()
        
        # 记录下载日志
        log_operation(
            request, 
            'download', 
            file=file
        )
        
        # 提供文件下载
        if not file.file:
            return Response(
                {'error': '文件不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = FileResponse(file.file.open('rb'))
        response['Content-Disposition'] = f'attachment; filename="{file.file_name}"'
        response['Content-Type'] = file.content_type or 'application/octet-stream'
        
        # 添加安全响应头
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        
        return response
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取文件统计数据"""
        user = request.user
        
        if hasattr(user, 'department') and user.department:
            user_departments = user.department.all()
            # 获取用户可见的文件
            queryset = ElectronicFile.objects.filter(
                Q(department__in=user_departments) | 
                Q(recipients__recipient=user)
            ).distinct()
        else:
            queryset = ElectronicFile.objects.filter(recipients__recipient=user)
        
        # 统计各状态文件数量
        total = queryset.count()
        draft = queryset.filter(status='draft').count()
        signed = queryset.filter(status='signed').count()
        sent = queryset.filter(status='sent').count()
        revoked = queryset.filter(status='revoked').count()
        
        return Response({
            'total': total,
            'draft': draft,
            'signed': signed,
            'sent': sent,
            'revoked': revoked
        })
    
    def destroy(self, request, *args, **kwargs):
        """删除文件"""
        file = self.get_object()
        user = request.user
        
        # 检查权限
        if user not in file.department.user_set.all():
            return Response(
                {'error': '无权删除此文件'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 记录删除日志
        log_operation(
            request, 
            'delete', 
            file=file
        )
        
        return super().destroy(request, *args, **kwargs)


class SignatureOperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """签章操作日志视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = SignatureOperationLogSerializer
    
    def get_queryset(self):
        user = self.request.user
        # 只返回用户所在部门的日志
        if hasattr(user, 'department') and user.department:
            user_departments = user.department.all()
            return SignatureOperationLog.objects.filter(department__in=user_departments)
        # 如果用户没有部门，返回空
        return SignatureOperationLog.objects.none()
