from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class RepairCategory(models.Model):
    """报修分类"""
    name = models.CharField('分类名称', max_length=50, unique=True)
    icon = models.CharField('图标', max_length=50, blank=True)
    description = models.TextField('描述', blank=True)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'repair_categories'
        verbose_name = '报修分类'
        verbose_name_plural = '报修分类'
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.name


class RepairApplication(models.Model):
    """报修申请"""
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待受理'),
        ('accepted', '已受理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('rejected', '已驳回'),
    ]
    
    # 基本信息
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='repair_applications',
        verbose_name='申请人'
    )
    category = models.ForeignKey(
        RepairCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='applications',
        verbose_name='报修分类'
    )
    title = models.CharField('报修标题', max_length=200)
    description = models.TextField('详细描述')
    location = models.CharField('报修地点', max_length=200)
    
    # 优先级和状态
    priority = models.CharField('优先级', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 联系方式
    contact_name = models.CharField('联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    
    # 图片附件
    images = models.JSONField('图片列表', default=list, blank=True)
    # 示例：[{"name": "image1.jpg", "url": "/media/...", "size": 1024}]
    
    # 处理信息
    handler = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_repairs',
        verbose_name='处理人'
    )
    accepted_at = models.DateTimeField('受理时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    
    # 处理意见
    handler_comment = models.TextField('处理意见', blank=True)
    applicant_comment = models.TextField('申请人评价', blank=True)
    rating = models.IntegerField('评分', null=True, blank=True)  # 1-5分
    
    # 扩展信息
    extra_data = models.JSONField('扩展数据', default=dict, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'repair_applications'
        verbose_name = '报修申请'
        verbose_name_plural = '报修申请'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority', 'created_at']),
            models.Index(fields=['applicant', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class RepairRecord(models.Model):
    """报修处理记录"""
    application = models.ForeignKey(
        RepairApplication,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='报修申请'
    )
    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='repair_records',
        verbose_name='操作人'
    )
    action = models.CharField('操作', max_length=50)  # 受理、处理中、完成等
    comment = models.TextField('备注', blank=True)
    images = models.JSONField('图片列表', default=list, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'repair_records'
        verbose_name = '报修处理记录'
        verbose_name_plural = '报修处理记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.application.title} - {self.action}"
