from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ResearchProject(models.Model):
    """科研项目"""
    PROJECT_TYPES = [
        ('national', '国家级'),
        ('provincial', '省级'),
        ('municipal', '市级'),
        ('university', '校级'),
        ('enterprise', '企业合作'),
    ]
    
    STATUS_CHOICES = [
        ('declared', '已申报'),
        ('approved', '已立项'),
        ('midterm', '中期检查'),
        ('final', '结题验收'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    project_code = models.CharField('项目编号', max_length=100, unique=True)
    project_name = models.CharField('项目名称', max_length=200)
    project_type = models.CharField('项目类型', max_length=20, choices=PROJECT_TYPES)
    
    # 负责人
    principal = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='principal_projects',
        verbose_name='项目负责人'
    )
    
    # 团队成员
    members = models.ManyToManyField(User, related_name='member_projects', blank=True)
    
    # 项目信息
    description = models.TextField('项目描述')
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='declared')
    
    # 经费信息
    total_budget = models.DecimalField('总经费', max_digits=12, decimal_places=2, default=0)
    used_budget = models.DecimalField('已使用经费', max_digits=12, decimal_places=2, default=0)
    budget_details = models.JSONField('经费明细', default=list, blank=True)
    # 示例：[{"category": "设备费", "amount": 10000, "used": 5000}]
    
    # 附件
    application_file = models.FileField('申报书', upload_to='research/projects/', blank=True, null=True)
    attachments = models.JSONField('附件列表', default=list, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'research_projects'
        verbose_name = '科研项目'
        verbose_name_plural = '科研项目'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.project_name


class ProjectMilestone(models.Model):
    """项目里程碑"""
    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name='项目'
    )
    name = models.CharField('里程碑名称', max_length=200)
    description = models.TextField('描述', blank=True)
    due_date = models.DateField('截止日期')
    completed_date = models.DateField('完成日期', null=True, blank=True)
    is_completed = models.BooleanField('是否完成', default=False)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'project_milestones'
        verbose_name = '项目里程碑'
        verbose_name_plural = '项目里程碑'
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.project.project_name} - {self.name}"


class ResearchAchievement(models.Model):
    """科研成果"""
    ACHIEVEMENT_TYPES = [
        ('paper', '论文'),
        ('patent', '专利'),
        ('book', '著作'),
        ('award', '获奖'),
        ('other', '其他'),
    ]
    
    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='achievements',
        verbose_name='关联项目'
    )
    achievement_type = models.CharField('成果类型', max_length=20, choices=ACHIEVEMENT_TYPES)
    title = models.CharField('标题', max_length=200)
    
    # 作者/完成人
    authors = models.ManyToManyField(User, related_name='research_achievements')
    first_author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='first_author_achievements',
        verbose_name='第一作者'
    )
    
    # 成果信息
    journal = models.CharField('期刊/出版社', max_length=200, blank=True)
    publish_date = models.DateField('发表/出版日期', null=True, blank=True)
    volume = models.CharField('卷/期', max_length=50, blank=True)
    page_range = models.CharField('页码', max_length=50, blank=True)
    doi = models.CharField('DOI', max_length=100, blank=True)
    
    # 附件
    file = models.FileField('成果文件', upload_to='research/achievements/', blank=True, null=True)
    
    # 审核
    is_verified = models.BooleanField('已审核', default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_achievements',
        verbose_name='审核人'
    )
    verified_at = models.DateTimeField('审核时间', null=True, blank=True)
    
    # 奖励关联
    reward_amount = models.DecimalField('奖励金额', max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'research_achievements'
        verbose_name = '科研成果'
        verbose_name_plural = '科研成果'
        ordering = ['-publish_date', '-created_at']
    
    def __str__(self):
        return self.title


class ResearchTeam(models.Model):
    """科研团队"""
    name = models.CharField('团队名称', max_length=200)
    description = models.TextField('团队简介', blank=True)
    leader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='led_teams',
        verbose_name='团队负责人'
    )
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    
    # 团队资料
    shared_files = models.JSONField('共享文件', default=list, blank=True)
    
    is_active = models.BooleanField('是否活跃', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'research_teams'
        verbose_name = '科研团队'
        verbose_name_plural = '科研团队'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class TeamTask(models.Model):
    """团队任务"""
    team = models.ForeignKey(
        ResearchTeam,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='团队'
    )
    title = models.CharField('任务标题', max_length=200)
    description = models.TextField('任务描述', blank=True)
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='负责人'
    )
    due_date = models.DateField('截止日期', null=True, blank=True)
    status = models.CharField(
        '状态',
        max_length=20,
        choices=[
            ('pending', '待开始'),
            ('in_progress', '进行中'),
            ('completed', '已完成'),
            ('cancelled', '已取消'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'team_tasks'
        verbose_name = '团队任务'
        verbose_name_plural = '团队任务'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.team.name} - {self.title}"


class TeamMeeting(models.Model):
    """团队会议"""
    team = models.ForeignKey(
        ResearchTeam,
        on_delete=models.CASCADE,
        related_name='meetings',
        verbose_name='团队'
    )
    title = models.CharField('会议主题', max_length=200)
    meeting_time = models.DateTimeField('会议时间')
    location = models.CharField('会议地点', max_length=200, blank=True)
    attendees = models.ManyToManyField(User, related_name='attended_meetings', blank=True)
    minutes = models.TextField('会议纪要', blank=True)
    attachments = models.JSONField('附件', default=list, blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_meetings',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'team_meetings'
        verbose_name = '团队会议'
        verbose_name_plural = '团队会议'
        ordering = ['-meeting_time']
    
    def __str__(self):
        return f"{self.team.name} - {self.title}"
