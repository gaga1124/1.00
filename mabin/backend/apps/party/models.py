from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PartyBranch(models.Model):
    """党支部/团支部"""
    BRANCH_TYPES = [
        ('party', '党支部'),
        ('league', '团支部'),
    ]
    name = models.CharField('支部名称', max_length=100)
    branch_type = models.CharField('类型', max_length=10, choices=BRANCH_TYPES)
    department = models.ForeignKey(
        'rbac.Department',
        on_delete=models.CASCADE,
        related_name='branches',
        verbose_name='所属部门'
    )
    secretary = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='led_branches',
        verbose_name='支部书记'
    )
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'party_branches'
        verbose_name = '支部'
        verbose_name_plural = '支部'

    def __str__(self):
        return f"{self.get_branch_type_display()} - {self.name}"

class PartyMember(models.Model):
    """党员/团员扩展信息"""
    MEMBER_TYPES = [
        ('member', '团员'),
        ('activist', '入党积极分子'),
        ('probationary', '预备党员'),
        ('party_member', '正式党员'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='party_info')
    branch = models.ForeignKey(PartyBranch, on_delete=models.SET_NULL, null=True, related_name='members')
    member_type = models.CharField('政治面貌', max_length=20, choices=MEMBER_TYPES)
    join_date = models.DateField('入党/入团日期', null=True, blank=True)
    introduction_date = models.DateField('确定积极分子日期', null=True, blank=True)
    probationary_date = models.DateField('转预备党员日期', null=True, blank=True)
    full_member_date = models.DateField('转正式党员日期', null=True, blank=True)
    
    volunteer_hours = models.DecimalField('志愿服务时长', max_digits=8, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'party_members'
        verbose_name = '党员团员信息'
        verbose_name_plural = '党员团员信息'

class PartyActivity(models.Model):
    """组织生活/志愿活动"""
    ACTIVITY_TYPES = [
        ('meeting', '组织生活会'),
        ('lesson', '党课/团课'),
        ('volunteer', '志愿活动'),
        ('other', '其他'),
    ]
    title = models.CharField('活动标题', max_length=200)
    activity_type = models.CharField('活动类型', max_length=20, choices=ACTIVITY_TYPES)
    branch = models.ForeignKey(PartyBranch, on_delete=models.CASCADE, related_name='activities')
    content = models.TextField('活动内容')
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    location = models.CharField('地点', max_length=200)
    
    participants = models.ManyToManyField(User, related_name='party_activities', blank=True)
    volunteer_hours_given = models.DecimalField('发放志愿时长', max_digits=5, decimal_places=1, default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'party_activities'
        verbose_name = '党团活动'
        verbose_name_plural = '党团活动'
