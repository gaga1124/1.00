from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Company(models.Model):
    """企业信息"""
    name = models.CharField('企业名称', max_length=200)
    industry = models.CharField('行业', max_length=100)
    scale = models.CharField(
        '规模',
        max_length=20,
        choices=[
            ('small', '小型（<50人）'),
            ('medium', '中型（50-500人）'),
            ('large', '大型（500-5000人）'),
            ('huge', '超大型（>5000人）'),
        ],
        default='medium'
    )
    address = models.CharField('地址', max_length=500)
    website = models.URLField('官网', blank=True)
    description = models.TextField('企业简介', blank=True)
    logo = models.ImageField('企业Logo', upload_to='companies/', blank=True, null=True)
    contact_person = models.CharField('联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    contact_email = models.EmailField('联系邮箱', blank=True)
    is_verified = models.BooleanField('已认证', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'companies'
        verbose_name = '企业'
        verbose_name_plural = '企业'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class JobPosting(models.Model):
    """招聘信息"""
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='job_postings',
        verbose_name='企业'
    )
    title = models.CharField('职位名称', max_length=200)
    department = models.CharField('部门', max_length=100, blank=True)
    job_type = models.CharField(
        '工作类型',
        max_length=20,
        choices=[
            ('fulltime', '全职'),
            ('parttime', '兼职'),
            ('internship', '实习'),
        ],
        default='fulltime'
    )
    salary_min = models.IntegerField('最低薪资', null=True, blank=True)
    salary_max = models.IntegerField('最高薪资', null=True, blank=True)
    location = models.CharField('工作地点', max_length=200)
    description = models.TextField('职位描述')
    requirements = models.TextField('任职要求')
    benefits = models.TextField('福利待遇', blank=True)
    deadline = models.DateField('截止日期', null=True, blank=True)
    is_active = models.BooleanField('是否有效', default=True)
    views_count = models.IntegerField('浏览次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'job_postings'
        verbose_name = '招聘信息'
        verbose_name_plural = '招聘信息'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"


class Resume(models.Model):
    """简历"""
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='resumes',
        verbose_name='学生'
    )
    name = models.CharField('简历名称', max_length=100)
    personal_info = models.JSONField('个人信息', default=dict, blank=True)
    education = models.JSONField('教育经历', default=list, blank=True)
    experience = models.JSONField('工作/实习经历', default=list, blank=True)
    skills = models.JSONField('技能', default=list, blank=True)
    projects = models.JSONField('项目经历', default=list, blank=True)
    awards = models.JSONField('获奖情况', default=list, blank=True)
    self_introduction = models.TextField('自我介绍', blank=True)
    is_default = models.BooleanField('默认简历', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'resumes'
        verbose_name = '简历'
        verbose_name_plural = '简历'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.name}"


class JobApplication(models.Model):
    """职位申请"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('viewed', '已查看'),
        ('interview', '面试中'),
        ('offer', '已录用'),
        ('rejected', '已拒绝'),
    ]
    
    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='职位'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='job_applications',
        verbose_name='学生'
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.SET_NULL,
        null=True,
        related_name='applications',
        verbose_name='简历'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    cover_letter = models.TextField('求职信', blank=True)
    applied_at = models.DateTimeField('申请时间', auto_now_add=True)
    viewed_at = models.DateTimeField('查看时间', null=True, blank=True)
    
    class Meta:
        db_table = 'job_applications'
        verbose_name = '职位申请'
        verbose_name_plural = '职位申请'
        unique_together = ['job', 'student']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.job.title}"


class JobFair(models.Model):
    """招聘会"""
    name = models.CharField('招聘会名称', max_length=200)
    description = models.TextField('描述', blank=True)
    location = models.CharField('地点', max_length=200)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    max_participants = models.IntegerField('最大参与人数', default=500)
    current_participants = models.IntegerField('当前参与人数', default=0)
    companies = models.ManyToManyField(Company, related_name='job_fairs', blank=True)
    is_active = models.BooleanField('是否有效', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'job_fairs'
        verbose_name = '招聘会'
        verbose_name_plural = '招聘会'
        ordering = ['-start_time']
    
    def __str__(self):
        return self.name


class JobFairRegistration(models.Model):
    """招聘会报名"""
    job_fair = models.ForeignKey(
        JobFair,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='招聘会'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='job_fair_registrations',
        verbose_name='学生'
    )
    registered_at = models.DateTimeField('报名时间', auto_now_add=True)
    
    class Meta:
        db_table = 'job_fair_registrations'
        verbose_name = '招聘会报名'
        verbose_name_plural = '招聘会报名'
        unique_together = ['job_fair', 'student']
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.job_fair.name}"


class EmploymentStatistics(models.Model):
    """就业统计数据"""
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='employment_stats',
        verbose_name='学生'
    )
    employment_status = models.CharField(
        '就业状态',
        max_length=20,
        choices=[
            ('employed', '已就业'),
            ('unemployed', '待就业'),
            ('graduate', '升学'),
            ('entrepreneur', '自主创业'),
            ('other', '其他'),
        ]
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='就业单位'
    )
    position = models.CharField('职位', max_length=200, blank=True)
    salary = models.IntegerField('薪资', null=True, blank=True)
    location = models.CharField('工作地点', max_length=200, blank=True)
    employment_date = models.DateField('就业日期', null=True, blank=True)
    source = models.CharField(
        '就业来源',
        max_length=20,
        choices=[
            ('job_fair', '招聘会'),
            ('online', '网络招聘'),
            ('recommendation', '推荐'),
            ('other', '其他'),
        ],
        blank=True
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'employment_statistics'
        verbose_name = '就业统计'
        verbose_name_plural = '就业统计'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.get_employment_status_display()}"
