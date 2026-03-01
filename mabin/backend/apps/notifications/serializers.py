from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification, NotificationRead, NotificationAttachment, NotificationSetting, NotificationLog

User = get_user_model()


class NotificationAttachmentSerializer(serializers.ModelSerializer):
    """通知附件序列化器"""
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationAttachment
        fields = ['id', 'filename', 'file_size', 'file_size_display', 'file_type', 'file_url']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_type(self, obj):
        """获取文件类型"""
        if obj.filename:
            ext = obj.filename.split('.')[-1].lower()
            type_map = {
                'pdf': 'pdf',
                'doc': 'word', 'docx': 'word',
                'xls': 'excel', 'xlsx': 'excel',
                'ppt': 'ppt', 'pptx': 'ppt',
                'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image',
                'mp4': 'video', 'avi': 'video',
                'mp3': 'audio',
                'zip': 'zip', 'rar': 'zip', '7z': 'zip',
            }
            return type_map.get(ext, 'other')
        return 'other'
    
    def get_file_size_display(self, obj):
        """格式化文件大小"""
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.2f} KB"
        else:
            return f"{obj.file_size / (1024 * 1024):.2f} MB"


class UserBriefSerializer(serializers.ModelSerializer):
    """用户简要信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name']


class NotificationReadSerializer(serializers.ModelSerializer):
    """通知阅读记录序列化器"""
    user = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = NotificationRead
        fields = ['id', 'user', 'is_read', 'read_at', 'read_device', 'is_handled', 'handled_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """通知列表序列化器"""
    sender = UserBriefSerializer(read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    business_type_display = serializers.CharField(source='get_business_type_display', read_only=True)
    is_read = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()
    need_action = serializers.BooleanField()
    action_status = serializers.CharField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'content', 'sender', 'priority', 'priority_display',
            'status', 'status_display', 'business_type', 'business_type_display',
            'business_action', 'link_url', 'link_params', 'need_action', 'action_status',
            'created_at', 'sent_at', 'recalled_at', 'expire_at',
            'total_recipients', 'read_count', 'unread_count', 'is_read', 'attachment_count'
        ]
    
    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            read_record = obj.read_records.filter(user=request.user).first()
            return read_record.is_read if read_record else False
        return False
    
    def get_attachment_count(self, obj):
        return obj.attachments.count()


class NotificationDetailSerializer(serializers.ModelSerializer):
    """通知详情序列化器"""
    sender = UserBriefSerializer(read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    business_type_display = serializers.CharField(source='get_business_type_display', read_only=True)
    attachments = NotificationAttachmentSerializer(many=True, read_only=True)
    is_read = serializers.SerializerMethodField()
    can_recall = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    need_action = serializers.BooleanField()
    is_handled = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'content', 'sender', 'notification_type', 'type_display',
            'business_type', 'business_type_display', 'business_id', 'business_model', 
            'business_action', 'link_url', 'link_params', 'need_action', 'action_status',
            'priority', 'priority_display', 'status', 'status_display',
            'created_at', 'sent_at', 'recalled_at', 'expire_at',
            'total_recipients', 'read_count', 'unread_count',
            'attachments', 'is_read', 'can_recall', 'can_delete', 'is_handled',
            'recipient_roles', 'recipient_departments'
        ]
    
    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            read_record = obj.read_records.filter(user=request.user).first()
            return read_record.is_read if read_record else False
        return False
    
    def get_is_handled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            read_record = obj.read_records.filter(user=request.user).first()
            return read_record.is_handled if read_record else False
        return False
    
    def get_can_recall(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user and obj.status == 'sent'
        return False
    
    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user or request.user.is_superuser
        return False


class NotificationCreateSerializer(serializers.ModelSerializer):
    """通知创建序列化器"""
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        default=list
    )
    attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        default=list
    )
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'content', 'notification_type', 'priority', 'business_type',
            'recipient_ids', 'recipient_roles', 'recipient_departments', 'attachments'
        ]
    
    def create(self, validated_data):
        recipient_ids = validated_data.pop('recipient_ids', [])
        attachments = validated_data.pop('attachments', [])
        
        # 创建通知
        notification = Notification.objects.create(
            sender=self.context['request'].user,
            status='draft',
            **validated_data
        )
        
        # 设置接收人
        if recipient_ids:
            notification.recipients.set(User.objects.filter(id__in=recipient_ids))
        
        # 保存附件
        for file in attachments:
            NotificationAttachment.objects.create(
                notification=notification,
                file=file,
                filename=file.name,
                file_size=file.size
            )
        
        return notification


class NotificationStatsSerializer(serializers.Serializer):
    """通知统计序列化器"""
    total_recipients = serializers.IntegerField()
    read_count = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    read_rate = serializers.FloatField()
    read_users = NotificationReadSerializer(many=True)
    unread_users = UserBriefSerializer(many=True)


class MarkAsReadSerializer(serializers.Serializer):
    """标记已读序列化器"""
    device = serializers.CharField(max_length=50, required=False, default='')


class NotificationSettingSerializer(serializers.ModelSerializer):
    """通知设置序列化器"""
    class Meta:
        model = NotificationSetting
        fields = [
            'id', 'workflow_enabled', 'file_enabled', 'academic_enabled',
            'warning_enabled', 'activity_enabled', 'repair_enabled',
            'resource_enabled', 'award_enabled', 'career_enabled',
            'party_enabled', 'research_enabled', 'email_enabled',
            'sms_enabled', 'push_enabled', 'dnd_enabled',
            'dnd_start_time', 'dnd_end_time'
        ]


class NotificationSummarySerializer(serializers.Serializer):
    """通知摘要序列化器 - 用于头部通知中心"""
    unread_count = serializers.IntegerField()
    todo_count = serializers.IntegerField()
    recent_notifications = NotificationListSerializer(many=True)
    

class NotificationFilterSerializer(serializers.Serializer):
    """通知筛选序列化器"""
    business_type = serializers.ChoiceField(
        choices=Notification.BUSINESS_TYPE_CHOICES,
        required=False
    )
    priority = serializers.ChoiceField(
        choices=Notification.PRIORITY_CHOICES,
        required=False
    )
    is_read = serializers.BooleanField(required=False)
    need_action = serializers.BooleanField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)


class NotificationLogSerializer(serializers.ModelSerializer):
    """通知操作日志序列化器"""
    user_name = serializers.CharField(source='user.real_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'action', 'action_display', 'user', 'user_name', 'user_username',
            'notification', 'notification_title', 'ip_address', 'user_agent',
            'details', 'created_at'
        ]
