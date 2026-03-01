from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ResourceCategory(models.Model):
    """资源分类"""
    name = models.CharField('分类名称', max_length=50, unique=True)
    description = models.TextField('描述', blank=True)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'resource_categories'
        verbose_name = '资源分类'
        verbose_name_plural = '资源分类'
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.name


class Resource(models.Model):
    """资源（会议室、报告厅、实验室等）"""
    RESOURCE_TYPES = [
        ('meeting_room', '会议室'),
        ('lecture_hall', '学术报告厅'),
        ('laboratory', '实验室'),
        ('classroom', '教室'),
        ('other', '其他'),
    ]
    
    name = models.CharField('资源名称', max_length=100)
    resource_type = models.CharField('资源类型', max_length=20, choices=RESOURCE_TYPES)
    category = models.ForeignKey(
        ResourceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resources',
        verbose_name='分类'
    )
    department = models.ForeignKey(
        'rbac.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resources',
        verbose_name='归属部门'
    )
    location = models.CharField('位置', max_length=200, blank=True)
    capacity = models.IntegerField('容纳人数', default=0)
    equipment = models.JSONField('设备配置', default=list, blank=True)
    # 示例：[{"name": "投影仪", "count": 1}, {"name": "白板", "count": 1}]
    
    description = models.TextField('描述', blank=True)
    images = models.JSONField('图片列表', default=list, blank=True)
    
    # 预约规则
    advance_booking_days = models.IntegerField('提前预约天数', default=30)
    min_booking_hours = models.DecimalField('最小预约时长（小时）', max_digits=3, decimal_places=1, default=0.5)
    max_booking_hours = models.DecimalField('最大预约时长（小时）', max_digits=4, decimal_places=1, default=8.0)
    
    # 是否需要审批
    require_approval = models.BooleanField('需要审批', default=True)
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_resources',
        verbose_name='审批人'
    )
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'resources'
        verbose_name = '资源'
        verbose_name_plural = '资源'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ResourceBooking(models.Model):
    """资源预约"""
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已驳回'),
        ('cancelled', '已取消'),
        ('completed', '已完成'),
    ]
    
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='资源'
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resource_bookings',
        verbose_name='申请人'
    )
    title = models.CharField('预约标题', max_length=200)
    description = models.TextField('描述', blank=True)
    
    # 时间
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 审批信息
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_bookings',
        verbose_name='审批人'
    )
    approval_comment = models.TextField('审批意见', blank=True)
    approval_time = models.DateTimeField('审批时间', null=True, blank=True)
    
    # 联系人信息
    contact_name = models.CharField('联系人', max_length=50, blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)
    
    # 附件
    attachments = models.JSONField('附件列表', default=list, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'resource_bookings'
        verbose_name = '资源预约'
        verbose_name_plural = '资源预约'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resource', 'start_time', 'end_time']),
        ]
    
    def __str__(self):
        return f"{self.resource.name} - {self.title}"
