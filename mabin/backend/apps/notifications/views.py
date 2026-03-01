from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from django.http import FileResponse
from django.core.cache import cache
from .models import Notification, NotificationRead, NotificationAttachment, NotificationSetting, NotificationLog
from .serializers import (
    NotificationListSerializer, NotificationDetailSerializer,
    NotificationCreateSerializer, NotificationStatsSerializer,
    MarkAsReadSerializer, NotificationAttachmentSerializer,
    NotificationSettingSerializer, NotificationSummarySerializer,
    NotificationFilterSerializer, NotificationLogSerializer
)
from .utils import get_user_unread_count, get_user_todo_count, mark_all_as_read
from .security import (
    RateLimiter, ContentSecurityChecker, SecurityLogger, get_client_ip
)


class NotificationViewSet(viewsets.ModelViewSet):
    """通知视图集 - 增强安全版本"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'priority', 'sent_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        action = self.action
        
        if action in ['sent', 'draft']:
            # 我发送的通知
            return Notification.objects.filter(sender=user)
        elif action == 'list':
            # 我接收的通知
            queryset = Notification.objects.filter(
                recipients=user,
                status__in=['sent', 'recalled']
            ).distinct()
            
            # 业务类型筛选
            business_type = self.request.query_params.get('business_type')
            if business_type:
                queryset = queryset.filter(business_type=business_type)
            
            # 优先级筛选
            priority = self.request.query_params.get('priority')
            if priority:
                queryset = queryset.filter(priority=priority)
            
            # 是否已读筛选
            is_read = self.request.query_params.get('is_read')
            if is_read is not None:
                if is_read.lower() == 'true':
                    queryset = queryset.filter(
                        read_records__user=user,
                        read_records__is_read=True
                    )
                else:
                    queryset = queryset.exclude(
                        read_records__user=user,
                        read_records__is_read=True
                    )
            
            # 待办筛选
            need_action = self.request.query_params.get('need_action')
            if need_action is not None:
                if need_action.lower() == 'true':
                    queryset = queryset.filter(need_action=True)
                    queryset = queryset.exclude(
                        read_records__user=user,
                        read_records__is_handled=True
                    )
            
            # 日期范围筛选
            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')
            if start_date:
                queryset = queryset.filter(created_at__date__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__date__lte=end_date)
            
            return queryset
        else:
            # 详情、更新等操作
            return Notification.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return NotificationCreateSerializer
        return NotificationDetailSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save()
    
    def create(self, request, *args, **kwargs):
        """创建通知 - 带频率限制和内容安全检查"""
        # 频率限制检查
        allowed, remaining, reset_time = RateLimiter.check(
            'create_draft', request.user.id
        )
        if not allowed:
            SecurityLogger.log_suspicious_activity(
                request.user,
                'rate_limit_exceeded',
                {'action': 'create_notification'},
                get_client_ip(request)
            )
            return RateLimiter.get_limit_response('create_draft', reset_time)
        
        # 内容安全检查
        title = request.data.get('title', '')
        content = request.data.get('content', '')
        
        # 检查敏感词
        title_pass, title_words = ContentSecurityChecker.check_sensitive_words(title)
        content_pass, content_words = ContentSecurityChecker.check_sensitive_words(content)
        
        if not title_pass or not content_pass:
            all_words = list(set(title_words + content_words))
            SecurityLogger.log_suspicious_activity(
                request.user,
                'sensitive_content_detected',
                {'title': title, 'sensitive_words': all_words},
                get_client_ip(request)
            )
            return Response(
                {'error': f'内容包含敏感词: {", ".join(all_words)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 清理内容中的危险标签
        if content:
            request.data['content'] = ContentSecurityChecker.sanitize_content(content)
        
        response = super().create(request, *args, **kwargs)
        
        # 记录操作日志
        if response.status_code == 201:
            notification_id = response.data.get('id')
            if notification_id:
                notification = Notification.objects.get(id=notification_id)
                SecurityLogger.log_notification_create(
                    request.user,
                    notification,
                    get_client_ip(request)
                )
        
        return response
    
    @action(detail=False, methods=['get'])
    def sent(self, request):
        """获取我发送的通知"""
        queryset = self.get_queryset().filter(sender=request.user).exclude(status='draft')
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        serializer = NotificationListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def draft(self, request):
        """获取草稿箱"""
        queryset = self.get_queryset().filter(sender=request.user, status='draft')
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        serializer = NotificationListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读通知数量"""
        count = get_user_unread_count(request.user)
        todo_count = get_user_todo_count(request.user)
        return Response({
            'unread_count': count,
            'todo_count': todo_count
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取通知摘要 - 用于头部通知中心"""
        user = request.user
        
        # 未读数量
        unread_count = get_user_unread_count(user)
        
        # 待办数量
        todo_count = get_user_todo_count(user)
        
        # 最近通知（最近5条）
        recent_notifications = Notification.objects.filter(
            recipients=user,
            status='sent'
        ).order_by('-created_at')[:5]
        
        data = {
            'unread_count': unread_count,
            'todo_count': todo_count,
            'recent_notifications': NotificationListSerializer(
                recent_notifications, many=True, context={'request': request}
            ).data
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def todos(self, request):
        """获取待办通知列表"""
        user = request.user
        queryset = Notification.objects.filter(
            recipients=user,
            status='sent',
            need_action=True
        ).exclude(
            read_records__user=user,
            read_records__is_handled=True
        ).distinct()
        
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        serializer = NotificationListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """标记所有通知为已读"""
        count = mark_all_as_read(request.user)
        
        # 记录批量标记日志
        SecurityLogger.log_batch_mark_read(
            request.user,
            count,
            get_client_ip(request),
            request
        )
        
        return Response({'message': f'已标记 {count} 条通知为已读'})
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """发送通知 - 带频率限制"""
        # 频率限制检查
        allowed, remaining, reset_time = RateLimiter.check(
            'send_notification', request.user.id
        )
        if not allowed:
            SecurityLogger.log_suspicious_activity(
                request.user,
                'rate_limit_exceeded',
                {'action': 'send_notification'},
                get_client_ip(request)
            )
            return RateLimiter.get_limit_response('send_notification', reset_time)
        
        notification = self.get_object()
        
        # 检查权限
        if notification.sender != request.user and not request.user.is_superuser:
            return Response({'error': '无权发送此通知'}, status=status.HTTP_403_FORBIDDEN)
        
        if notification.status != 'draft':
            return Response({'error': '只能发送草稿状态的通知'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查接收人数量限制（防止滥用）
        if notification.notification_type not in ['all']:
            recipient_count = notification.recipients.count()
            if recipient_count == 0:
                return Response({'error': '请至少选择一个接收人'}, status=status.HTTP_400_BAD_REQUEST)
            
            max_recipients = 10000  # 最大接收人数限制
            if recipient_count > max_recipients:
                return Response(
                    {'error': f'接收人数超过限制，最多{max_recipients}人'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        notification.send()
        
        # 记录操作日志
        SecurityLogger.log_notification_send(
            request.user,
            notification,
            get_client_ip(request)
        )
        
        serializer = NotificationDetailSerializer(notification, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def recall(self, request, pk=None):
        """撤回通知"""
        notification = self.get_object()
        
        # 检查权限
        if notification.sender != request.user and not request.user.is_superuser:
            return Response({'error': '无权撤回此通知'}, status=status.HTTP_403_FORBIDDEN)
        
        if notification.status != 'sent':
            return Response({'error': '只能撤回已发送的通知'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查撤回时间限制（24小时内可撤回）
        if notification.sent_at:
            time_diff = timezone.now() - notification.sent_at
            if time_diff.total_seconds() > 24 * 3600:
                return Response(
                    {'error': '通知发送超过24小时，无法撤回'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        notification.recall()
        
        # 记录操作日志
        SecurityLogger.log_notification_recall(
            request.user,
            notification,
            get_client_ip(request)
        )
        
        serializer = NotificationDetailSerializer(notification, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """标记通知为已读 - 带频率限制"""
        # 频率限制检查
        allowed, remaining, reset_time = RateLimiter.check(
            'mark_as_read', request.user.id
        )
        if not allowed:
            return RateLimiter.get_limit_response('mark_as_read', reset_time)
        
        notification = self.get_object()
        
        # 检查用户是否是接收人
        if request.user not in notification.recipients.all():
            return Response({'error': '无权操作此通知'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MarkAsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = serializer.validated_data.get('device', '')
        
        read_record, created = NotificationRead.objects.get_or_create(
            notification=notification,
            user=request.user
        )
        
        if not read_record.is_read:
            read_record.mark_as_read(device=device)
            
            # 记录标记已读日志
            SecurityLogger.log_mark_as_read(
                request.user,
                notification,
                get_client_ip(request),
                request
            )
        
        return Response({'message': '已标记为已读'})
    
    @action(detail=True, methods=['post'])
    def handle(self, request, pk=None):
        """处理待办通知"""
        notification = self.get_object()
        user = request.user
        
        # 检查用户是否是接收人
        if user not in notification.recipients.all():
            return Response({'error': '无权操作此通知'}, status=status.HTTP_403_FORBIDDEN)
        
        # 检查是否需要处理
        if not notification.need_action:
            return Response({'error': '此通知不需要处理'}, status=status.HTTP_400_BAD_REQUEST)
        
        read_record, created = NotificationRead.objects.get_or_create(
            notification=notification,
            user=user
        )
        
        if not read_record.is_handled:
            read_record.mark_as_handled()
            
            # 记录标记已处理日志
            SecurityLogger.log_mark_as_handled(
                request.user,
                notification,
                get_client_ip(request),
                request
            )
        
        return Response({'message': '已标记为已处理'})
    
    @action(detail=False, methods=['post'])
    def batch_mark_as_read(self, request):
        """批量标记已读 - 带频率限制"""
        # 频率限制检查
        allowed, remaining, reset_time = RateLimiter.check(
            'batch_operation', request.user.id
        )
        if not allowed:
            return RateLimiter.get_limit_response('batch_operation', reset_time)
        
        notification_ids = request.data.get('notification_ids', [])
        if not notification_ids:
            return Response({'error': '请选择要标记的通知'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 限制批量操作数量
        if len(notification_ids) > 100:
            return Response(
                {'error': '批量操作数量不能超过100条'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证所有通知是否都是当前用户的
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            recipients=request.user,
            status='sent'
        )
        
        if notifications.count() != len(notification_ids):
            return Response(
                {'error': '包含无权操作的通知'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 批量标记
        count = 0
        for notification in notifications:
            read_record, created = NotificationRead.objects.get_or_create(
                notification=notification,
                user=request.user
            )
            if not read_record.is_read:
                read_record.mark_as_read()
                count += 1
        
        # 记录批量标记日志
        SecurityLogger.log_batch_mark_read(
            request.user,
            count,
            get_client_ip(request),
            request
        )
        
        return Response({'message': f'已标记 {count} 条通知为已读'})
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """获取通知阅读统计"""
        notification = self.get_object()
        
        # 检查权限（只有发送者和管理员可以查看统计）
        if notification.sender != request.user and not request.user.is_superuser:
            return Response({'error': '无权查看此通知的统计'}, status=status.HTTP_403_FORBIDDEN)
        
        read_records = notification.read_records.all()
        read_users = read_records.filter(is_read=True)
        
        # 获取未读用户
        read_user_ids = read_users.values_list('user_id', flat=True)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        unread_users = User.objects.filter(
            id__in=notification.recipients.values_list('id', flat=True)
        ).exclude(id__in=read_user_ids)
        
        total = notification.total_recipients
        read_count = read_users.count()
        unread_count = total - read_count
        read_rate = (read_count / total * 100) if total > 0 else 0
        
        data = {
            'total_recipients': total,
            'read_count': read_count,
            'unread_count': unread_count,
            'read_rate': round(read_rate, 2),
            'read_users': read_users,
            'unread_users': unread_users
        }
        
        serializer = NotificationStatsSerializer(data)
        
        # 记录查看统计日志
        SecurityLogger.log_view_stats(
            request.user,
            notification,
            get_client_ip(request),
            request
        )
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_attachment(self, request, pk=None):
        """上传附件 - 带安全检查和频率限制"""
        # 频率限制检查
        allowed, remaining, reset_time = RateLimiter.check(
            'upload_attachment', request.user.id
        )
        if not allowed:
            SecurityLogger.log_suspicious_activity(
                request.user,
                'rate_limit_exceeded',
                {'action': 'upload_attachment'},
                get_client_ip(request)
            )
            return RateLimiter.get_limit_response('upload_attachment', reset_time)
        
        notification = self.get_object()
        
        # 检查权限
        if notification.sender != request.user:
            return Response({'error': '无权上传附件'}, status=status.HTTP_403_FORBIDDEN)
        
        if notification.status != 'draft':
            return Response({'error': '只能为草稿状态的通知上传附件'}, status=status.HTTP_400_BAD_REQUEST)
        
        files = request.FILES.getlist('files')
        if not files:
            return Response({'error': '请选择要上传的文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 限制单次上传数量
        if len(files) > 10:
            return Response(
                {'error': '单次最多上传10个文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attachments = []
        errors = []
        
        for file in files:
            # 检查文件类型
            type_allowed, type_error = ContentSecurityChecker.check_file_type(file)
            if not type_allowed:
                errors.append(f'{file.name}: {type_error}')
                continue
            
            # 检查文件大小
            size_allowed, size_error = ContentSecurityChecker.check_file_size(file)
            if not size_allowed:
                errors.append(f'{file.name}: {size_error}')
                continue
            
            # 检查重复文件（通过哈希）
            file_hash = ContentSecurityChecker.calculate_file_hash(file)
            cache_key = f"notification_file_hash:{file_hash}"
            if cache.get(cache_key):
                errors.append(f'{file.name}: 该文件已存在')
                continue
            
            # 保存文件
            attachment = NotificationAttachment.objects.create(
                notification=notification,
                file=file,
                filename=file.name,
                file_size=file.size
            )
            attachments.append(attachment)
            
            # 缓存文件哈希（24小时）
            cache.set(cache_key, True, 24 * 3600)
            
            # 记录上传日志
            SecurityLogger.log_attachment_upload(
                request.user,
                attachment,
                get_client_ip(request)
            )
        
        if errors and not attachments:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = NotificationAttachmentSerializer(
            attachments, many=True, context={'request': request}
        )
        
        response_data = {'data': serializer.data}
        if errors:
            response_data['warnings'] = errors
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """删除通知"""
        notification = self.get_object()
        
        # 检查权限
        if notification.sender != request.user and not request.user.is_superuser:
            return Response({'error': '无权删除此通知'}, status=status.HTTP_403_FORBIDDEN)
        
        # 软删除
        notification.status = 'deleted'
        notification.save()
        
        # 记录删除日志
        SecurityLogger.log_notification_delete(
            request.user,
            notification,
            get_client_ip(request),
            request
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationSettingViewSet(viewsets.ViewSet):
    """通知设置视图集"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_settings(self, request):
        """获取当前用户的通知设置"""
        setting, created = NotificationSetting.objects.get_or_create(user=request.user)
        serializer = NotificationSettingSerializer(setting)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def update_settings(self, request):
        """更新通知设置"""
        setting, created = NotificationSetting.objects.get_or_create(user=request.user)
        serializer = NotificationSettingSerializer(setting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # 记录更新设置日志
        SecurityLogger.log_update_settings(
            request.user,
            request.data,
            get_client_ip(request),
            request
        )
        
        return Response(serializer.data)


class NotificationAttachmentViewSet(viewsets.ViewSet):
    """通知附件视图集 - 增强安全版本"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """下载附件 - 带权限检查和日志"""
        try:
            attachment = NotificationAttachment.objects.get(pk=pk)
        except NotificationAttachment.DoesNotExist:
            return Response({'error': '附件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查权限（接收人或发送人可以下载）
        notification = attachment.notification
        if (request.user not in notification.recipients.all() and 
            notification.sender != request.user and 
            not request.user.is_superuser):
            SecurityLogger.log_suspicious_activity(
                request.user,
                'unauthorized_download_attempt',
                {'attachment_id': pk, 'notification_id': notification.id},
                get_client_ip(request)
            )
            return Response({'error': '无权下载此附件'}, status=status.HTTP_403_FORBIDDEN)
        
        # 已撤回的通知不能下载附件
        if notification.status == 'recalled':
            return Response({'error': '该通知已撤回，无法下载附件'}, status=status.HTTP_403_FORBIDDEN)
        
        if not attachment.file:
            return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 记录下载日志
        SecurityLogger.log_attachment_download(
            request.user,
            attachment,
            get_client_ip(request),
            request
        )
        
        response = FileResponse(attachment.file.open('rb'))
        response['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
        response['Content-Type'] = 'application/octet-stream'
        
        # 添加安全响应头
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        
        return response
    
    @action(detail=True, methods=['delete'])
    def delete(self, request, pk=None):
        """删除附件"""
        try:
            attachment = NotificationAttachment.objects.get(pk=pk)
        except NotificationAttachment.DoesNotExist:
            return Response({'error': '附件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查权限
        if attachment.notification.sender != request.user:
            return Response({'error': '无权删除此附件'}, status=status.HTTP_403_FORBIDDEN)
        
        if attachment.notification.status != 'draft':
            return Response({'error': '只能删除草稿状态通知的附件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 清除文件哈希缓存
        file_hash = ContentSecurityChecker.calculate_file_hash(attachment.file)
        if file_hash:
            cache_key = f"notification_file_hash:{file_hash}"
            cache.delete(cache_key)
        
        # 记录删除附件日志
        SecurityLogger.log_attachment_delete(
            request.user,
            attachment.filename,
            attachment.notification,
            get_client_ip(request),
            request
        )
        
        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """通知操作日志视图集 - 仅管理员可查看"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationLogSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__real_name', 'details']
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        # 只有管理员可以查看所有日志
        if not user.is_staff and not user.is_superuser:
            # 普通用户只能查看自己的日志
            return NotificationLog.objects.filter(user=user)
        
        queryset = NotificationLog.objects.all()
        
        # 操作类型筛选
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # 用户筛选
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # 通知筛选
        notification_id = self.request.query_params.get('notification_id')
        if notification_id:
            queryset = queryset.filter(notification_id=notification_id)
        
        # 日期范围筛选
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset.select_related('user', 'notification')
    
    @action(detail=False, methods=['get'])
    def my_logs(self, request):
        """获取当前用户的操作日志"""
        queryset = NotificationLog.objects.filter(user=request.user)
        
        # 操作类型筛选
        action = request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # 日期范围筛选
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取日志统计信息 - 仅管理员"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({'error': '无权查看统计'}, status=status.HTTP_403_FORBIDDEN)
        
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        # 今日日志统计
        today = timezone.now().date()
        today_logs = NotificationLog.objects.filter(created_at__date=today)
        
        # 操作类型分布
        action_stats = NotificationLog.objects.values('action').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # 最近7天日志趋势
        last_7_days = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = NotificationLog.objects.filter(created_at__date=date).count()
            last_7_days.append({'date': date.isoformat(), 'count': count})
        
        # 活跃用户（操作最多的用户）
        active_users = NotificationLog.objects.values(
            'user__id', 'user__username', 'user__real_name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        data = {
            'today_total': today_logs.count(),
            'action_distribution': action_stats,
            'last_7_days_trend': list(reversed(last_7_days)),
            'active_users': active_users
        }
        
        return Response(data)
