from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SocialPractice(models.Model):
    """社会实践活动（三下乡、返家乡等）"""
    STATUS_CHOICES = [
        ('declared', '已申报'),
        ('approved', '已立项'),
        ('submitted', '成果提交'),
        ('completed', '已结项'),
        ('excellent', '评优'),
    ]
    title = models.CharField('活动标题', max_length=200)
    practice_type = models.CharField('实践类型', max_length=50)  # 三下乡, 返家乡
    team_name = models.CharField('团队名称', max_length=200, blank=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_practices')
    members = models.ManyToManyField(User, related_name='participated_practices', blank=True)
    
    description = models.TextField('活动简介')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='declared')
    
    report_file = models.FileField('活动报告', upload_to='activities/practice/reports/', blank=True, null=True)
    media_files = models.JSONField('媒体材料', default=list, blank=True)  # 照片、视频URL列表
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'social_practices'
        verbose_name = '社会实践'
        verbose_name_plural = '社会实践'

class Competition(models.Model):
    """学科竞赛"""
    title = models.CharField('竞赛名称', max_length=200)
    level = models.CharField('级别', max_length=50)  # 国家级、省级等
    organizer = models.CharField('主办单位', max_length=200)
    registration_deadline = models.DateTimeField('报名截止时间')
    
    is_active = models.BooleanField('是否开启', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'competitions'
        verbose_name = '学科竞赛'
        verbose_name_plural = '学科竞赛'

class CompetitionTeam(models.Model):
    """竞赛报名团队"""
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='teams')
    team_name = models.CharField('团队名称', max_length=200)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_competition_teams')
    members = models.ManyToManyField(User, related_name='competition_teams', blank=True)
    advisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='advised_teams', verbose_name='指导教师')
    
    work_file = models.FileField('参赛作品', upload_to='activities/competition/works/', blank=True, null=True)
    score = models.DecimalField('评分', max_digits=5, decimal_places=2, null=True, blank=True)
    award_level = models.CharField('获奖等级', max_length=50, blank=True)
    
    status = models.CharField('状态', max_length=20, default='registered')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'competition_teams'
        verbose_name = '竞赛报名'
        verbose_name_plural = '竞赛报名'

class DynamicActivityType(models.Model):
    """动态活动类型定义（元模型）"""
    name = models.CharField('活动名称', max_length=100, unique=True)
    code = models.CharField('活动编码', max_length=50, unique=True)  # 用于逻辑识别
    schema = models.JSONField('表单结构定义', default=dict)  # 定义需要的字段及其类型
    # 示例 schema: {"fields": [{"name": "location", "label": "地点", "type": "text"}, {"name": "budget", "label": "预算", "type": "number"}]}
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'dynamic_activity_types'
        verbose_name = '自定义活动类型'
        verbose_name_plural = '自定义活动类型'

    def __str__(self):
        return self.name

class DynamicActivityInstance(models.Model):
    """动态活动实例数据存储"""
    activity_type = models.ForeignKey(DynamicActivityType, on_delete=models.CASCADE, related_name='instances')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')
    data = models.JSONField('活动数据', default=dict)  # 存储具体的字段值
    # 示例 data: {"location": "会议室A", "budget": 500}
    
    status = models.CharField('状态', max_length=20, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'dynamic_activity_instances'
        verbose_name = '自定义活动数据'
        verbose_name_plural = '自定义活动数据'
