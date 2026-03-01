import os
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


def notification_attachment_path(instance, filename):
    """生成通知附件上传路径"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('notifications/attachments/', filename)


class Notification(models.Model):
    """通知模型 - 系统中枢神经，整合所有业务通知"""
    
    # 优先级选择
    PRIORITY_CHOICES = [
        ('normal', '普通'),
        ('important', '重要'),
        ('urgent', '紧急'),
    ]
    
    # 状态选择
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('sent', '已发送'),
        ('recalled', '已撤回'),
        ('deleted', '已删除'),
    ]
    
    # 通知类型选择
    TYPE_CHOICES = [
        ('all', '全员通知'),
        ('role', '按角色'),
        ('department', '按部门'),
        ('specific', '指定人员'),
    ]
    
    # 业务类型选择 - 新增
    BUSINESS_TYPE_CHOICES = [
        ('system', '系统通知'),
        ('workflow', '流程审批'),
        ('file', '文件签章'),
        ('academic', '教务通知'),
        ('warning', '预警提醒'),
        ('activity', '活动通知'),
        ('repair', '报修服务'),
        ('resource', '资源预约'),
        ('award', '评奖评优'),
        ('career', '就业服务'),
        ('party', '党建团建'),
        ('research', '科研管理'),
    ]
    
    # 基础信息
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name='发送人'
    )
    
    # 业务类型 - 新增
    business_type = models.CharField(
        '业务类型',
        max_length=20,
        choices=BUSINESS_TYPE_CHOICES,
        default='system'
    )
    
    # 业务关联 - 新增
    business_id = models.CharField('业务ID', max_length=100, blank=True, default='')
    business_model = models.CharField('业务模型', max_length=50, blank=True, default='')
    business_action = models.CharField('业务动作', max_length=50, blank=True, default='')
    
    # 跳转链接 - 新增
    link_url = models.CharField('跳转链接', max_length=500, blank=True, default='')
    link_params = models.JSONField('链接参数', default=dict, blank=True)
    
    # 接收人设置
    notification_type = models.CharField(
        '通知类型',
        max_length=20,
        choices=TYPE_CHOICES,
        default='specific'
    )
    recipients = models.ManyToManyField(
        User,
        related_name='received_notifications',
        verbose_name='接收人',
        blank=True
    )
    recipient_roles = models.JSONField('接收角色', default=list, blank=True)
    recipient_departments = models.JSONField('接收部门', default=list, blank=True)
    
    # 状态和等级
    priority = models.CharField(
        '重要等级',
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    sent_at = models.DateTimeField('发送时间', null=True, blank=True)
    recalled_at = models.DateTimeField('撤回时间', null=True, blank=True)
    
    # 阅读统计（缓存，实时计算）
    total_recipients = models.PositiveIntegerField('总接收人数', default=0)
    read_count = models.PositiveIntegerField('已读人数', default=0)
    
    # 过期时间 - 新增
    expire_at = models.DateTimeField('过期时间', null=True, blank=True)
    
    # 是否需要处理 - 新增（用于待办类通知）
    need_action = models.BooleanField('需要处理', default=False)
    action_status = models.CharField('处理状态', max_length=20, default='pending')
    
    class Meta:
        db_table = 'notifications'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business_type', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def send(self):
        """发送通知"""
        if self.status == 'draft':
            self.status = 'sent'
            self.sent_at = timezone.now()
            
            # 根据通知类型设置接收人
            if self.notification_type == 'all':
                self.recipients.set(User.objects.filter(is_active=True))
            elif self.notification_type == 'role' and self.recipient_roles:
                from apps.rbac.models import UserRole
                user_ids = UserRole.objects.filter(
                    role__code__in=self.recipient_roles
                ).values_list('user_id', flat=True).distinct()
                self.recipients.set(User.objects.filter(id__in=user_ids, is_active=True))
            elif self.notification_type == 'department' and self.recipient_departments:
                self.recipients.set(User.objects.filter(
                    department_id__in=self.recipient_departments,
                    is_active=True
                ))
            
            self.total_recipients = self.recipients.count()
            self.save()
            
            # 创建阅读记录
            self.create_read_records()
    
    def create_read_records(self):
        """为所有接收人创建阅读记录"""
        for recipient in self.recipients.all():
            NotificationRead.objects.get_or_create(
                notification=self,
                user=recipient
            )
    
    def recall(self):
        """撤回通知"""
        if self.status == 'sent':
            self.status = 'recalled'
            self.recalled_at = timezone.now()
            self.save()
    
    def update_read_stats(self):
        """更新阅读统计"""
        self.read_count = self.read_records.filter(is_read=True).count()
        self.save(update_fields=['read_count'])
    
    @property
    def unread_count(self):
        """未读人数"""
        return self.total_recipients - self.read_count
    
    @property
    def priority_display_class(self):
        """获取优先级对应的样式类"""
        priority_map = {
            'normal': 'info',
            'important': 'warning',
            'urgent': 'danger'
        }
        return priority_map.get(self.priority, 'info')
    
    @property
    def business_type_display(self):
        """获取业务类型显示名称"""
        type_map = dict(self.BUSINESS_TYPE_CHOICES)
        return type_map.get(self.business_type, '系统通知')
    
    @property
    def is_expired(self):
        """是否已过期"""
        if self.expire_at:
            return timezone.now() > self.expire_at
        return False


class NotificationRead(models.Model):
    """通知阅读记录模型 - 实现已读状态持久化和多端同步"""
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='read_records',
        verbose_name='通知'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_reads',
        verbose_name='用户'
    )
    is_read = models.BooleanField('是否已读', default=False)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    read_device = models.CharField('阅读设备', max_length=50, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    # 是否已处理 - 新增（用于待办类通知）
    is_handled = models.BooleanField('是否已处理', default=False)
    handled_at = models.DateTimeField('处理时间', null=True, blank=True)
    
    class Meta:
        db_table = 'notification_reads'
        verbose_name = '通知阅读记录'
        verbose_name_plural = '通知阅读记录'
        unique_together = ['notification', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.notification.title}"
    
    def mark_as_read(self, device=''):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.read_device = device
            self.save()
            # 更新通知的阅读统计
            self.notification.update_read_stats()
    
    def mark_as_handled(self):
        """标记为已处理"""
        if not self.is_handled:
            self.is_handled = True
            self.handled_at = timezone.now()
            self.save()


class NotificationAttachment(models.Model):
    """通知附件模型"""
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='通知'
    )
    file = models.FileField('文件', upload_to=notification_attachment_path)
    filename = models.CharField('原始文件名', max_length=255)
    file_size = models.PositiveIntegerField('文件大小', default=0)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    
    class Meta:
        db_table = 'notification_attachments'
        verbose_name = '通知附件'
        verbose_name_plural = '通知附件'


class NotificationSetting(models.Model):
    """通知设置模型 - 用户个性化通知设置"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_setting',
        verbose_name='用户'
    )
    
    # 各类通知的开关设置
    workflow_enabled = models.BooleanField('流程审批通知', default=True)
    file_enabled = models.BooleanField('文件签章通知', default=True)
    academic_enabled = models.BooleanField('教务通知', default=True)
    warning_enabled = models.BooleanField('预警提醒', default=True)
    activity_enabled = models.BooleanField('活动通知', default=True)
    repair_enabled = models.BooleanField('报修服务通知', default=True)
    resource_enabled = models.BooleanField('资源预约通知', default=True)
    award_enabled = models.BooleanField('评奖评优通知', default=True)
    career_enabled = models.BooleanField('就业服务通知', default=True)
    party_enabled = models.BooleanField('党建团建通知', default=True)
    research_enabled = models.BooleanField('科研管理通知', default=True)
    
    # 通知方式设置
    email_enabled = models.BooleanField('邮件通知', default=False)
    sms_enabled = models.BooleanField('短信通知', default=False)
    push_enabled = models.BooleanField('推送通知', default=True)
    
    # 免打扰设置
    dnd_enabled = models.BooleanField('免打扰模式', default=False)
    dnd_start_time = models.TimeField('免打扰开始时间', null=True, blank=True)
    dnd_end_time = models.TimeField('免打扰结束时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'notification_settings'
        verbose_name = '通知设置'
        verbose_name_plural = '通知设置'
    
    def __str__(self):
        return f"{self.user}的通知设置"
    
    def is_type_enabled(self, business_type):
        """检查某类通知是否开启"""
        type_map = {
            'workflow': self.workflow_enabled,
            'file': self.file_enabled,
            'academic': self.academic_enabled,
            'warning': self.warning_enabled,
            'activity': self.activity_enabled,
            'repair': self.repair_enabled,
            'resource': self.resource_enabled,
            'award': self.award_enabled,
            'career': self.career_enabled,
            'party': self.party_enabled,
            'research': self.research_enabled,
        }
        return type_map.get(business_type, True)
    
    def is_in_dnd_period(self):
        """检查当前是否在免打扰时间段"""
        if not self.dnd_enabled:
            return False
        
        from datetime import datetime, time
        now = datetime.now().time()
        
        if self.dnd_start_time and self.dnd_end_time:
            if self.dnd_start_time <= self.dnd_end_time:
                return self.dnd_start_time <= now <= self.dnd_end_time
            else:
                # 跨午夜的情况
                return now >= self.dnd_start_time or now <= self.dnd_end_time
        
        return False


class NotificationLog(models.Model):
    """通知操作日志模型 - 记录所有通知相关操作"""
    
    ACTION_CHOICES = [
        ('create', '创建通知'),
        ('send', '发送通知'),
        ('recall', '撤回通知'),
        ('delete', '删除通知'),
        ('update', '更新通知'),
        ('mark_as_read', '标记已读'),
        ('mark_as_handled', '标记已处理'),
        ('batch_mark_read', '批量标记已读'),
        ('upload_attachment', '上传附件'),
        ('download_attachment', '下载附件'),
        ('delete_attachment', '删除附件'),
        ('view_detail', '查看详情'),
        ('view_stats', '查看统计'),
        ('update_settings', '更新设置'),
        ('suspicious', '可疑活动'),
        ('rate_limit', '频率限制'),
        ('security_alert', '安全警告'),
    ]
    
    action = models.CharField('操作类型', max_length=30, choices=ACTION_CHOICES)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='通知',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_logs',
        verbose_name='操作用户'
    )
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', blank=True)
    details = models.JSONField('详细信息', default=dict, blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        db_table = 'notification_logs'
        verbose_name = '通知操作日志'
        verbose_name_plural = '通知操作日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['notification', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.created_at}"
