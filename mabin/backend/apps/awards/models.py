from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AwardType(models.Model):
    """奖项类型"""
    AWARD_CATEGORIES = [
        ('scholarship', '奖学金'),
        ('grant', '助学金'),
        ('honor', '荣誉称号'),
    ]
    
    name = models.CharField('奖项名称', max_length=100)
    category = models.CharField('奖项类别', max_length=20, choices=AWARD_CATEGORIES)
    level = models.CharField('级别', max_length=50, blank=True)  # 国家级、省级、校级等
    amount = models.DecimalField('金额', max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField('描述', blank=True)
    
    # 评选条件（JSON存储）
    criteria = models.JSONField('评选条件', default=dict, blank=True)
    # 示例：{"gpa_min": 3.5, "no_failures": true, "required_courses": []}
    
    # 评选设置
    is_active = models.BooleanField('是否启用', default=True)
    application_start = models.DateTimeField('申请开始时间', null=True, blank=True)
    application_end = models.DateTimeField('申请结束时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'award_types'
        verbose_name = '奖项类型'
        verbose_name_plural = '奖项类型'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class AwardApplication(models.Model):
    """评奖评优申请"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('reviewing', '审核中'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
        ('publicized', '已公示'),
        ('cancelled', '已取消'),
    ]
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='award_applications',
        verbose_name='学生'
    )
    award_type = models.ForeignKey(
        AwardType,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='奖项类型'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # 申请信息
    application_reason = models.TextField('申请理由')
    achievements = models.JSONField('主要成果', default=list, blank=True)
    # 示例：[{"type": "获奖", "title": "全国大学生数学建模竞赛一等奖", "date": "2024-01-01"}]
    
    # 附件
    attachments = models.JSONField('附件列表', default=list, blank=True)
    
    # 自动匹配结果
    match_score = models.DecimalField('匹配度', max_digits=5, decimal_places=2, null=True, blank=True)
    match_details = models.JSONField('匹配详情', default=dict, blank=True)
    
    # 审核信息
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_awards',
        verbose_name='审核人'
    )
    review_comment = models.TextField('审核意见', blank=True)
    review_time = models.DateTimeField('审核时间', null=True, blank=True)
    
    # 公示信息
    publicize_start = models.DateTimeField('公示开始时间', null=True, blank=True)
    publicize_end = models.DateTimeField('公示结束时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'award_applications'
        verbose_name = '评奖评优申请'
        verbose_name_plural = '评奖评优申请'
        ordering = ['-created_at']
        unique_together = ['student', 'award_type']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.award_type.name}"


class AwardPublicity(models.Model):
    """公示记录"""
    application = models.ForeignKey(
        AwardApplication,
        on_delete=models.CASCADE,
        related_name='publicities',
        verbose_name='申请'
    )
    title = models.CharField('公示标题', max_length=200)
    content = models.TextField('公示内容')
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    is_active = models.BooleanField('是否有效', default=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'award_publicities'
        verbose_name = '公示记录'
        verbose_name_plural = '公示记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
