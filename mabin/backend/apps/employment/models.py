from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Company(models.Model):
    """企业"""
    name = models.CharField('企业名称', max_length=200)
    industry = models.CharField('行业', max_length=100, blank=True)
    scale = models.CharField('规模', max_length=50, blank=True)  # 如：100-500人
    address = models.CharField('地址', max_length=200, blank=True)
    website = models.URLField('官网', blank=True)
    description = models.TextField('企业简介', blank=True)
    logo = models.ImageField('企业Logo', upload_to='employment/company/', blank=True, null=True)
    
    # 联系人信息
    contact_name = models.CharField('联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    contact_email = models.EmailField('联系邮箱', blank=True)
    
    is_verified = models.BooleanField('已认证', default=False)
    is_active = models.BooleanField('是否启用', default=True)
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
    
    # 职位要求
    job_description = models.TextField('职位描述')
    requirements = models.TextField('任职要求')
    salary_range = models.CharField('薪资范围', max_length=100, blank=True)
    location = models.CharField('工作地点', max_length=200)
    
    # 招聘信息
    recruitment_number = models.IntegerField('招聘人数', default=1)
    applied_count = models.IntegerField('已投递人数', default=0)
    
    # 时间信息
    publish_time = models.DateTimeField('发布时间', auto_now_add=True)
    deadline = models.DateTimeField('截止时间', null=True, blank=True)
    is_active = models.BooleanField('是否有效', default=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'job_postings'
        verbose_name = '招聘信息'
        verbose_name_plural = '招聘信息'
        ordering = ['-publish_time']
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"


class JobApplication(models.Model):
    """简历投递"""
    STATUS_CHOICES = [
        ('pending', '待查看'),
        ('viewed', '已查看'),
        ('interview', '面试中'),
        ('offer', '已录用'),
        ('rejected', '已拒绝'),
    ]
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='job_applications',
        verbose_name='学生'
    )
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='招聘信息'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 简历信息
    resume = models.FileField('简历', upload_to='employment/resumes/', blank=True, null=True)
    cover_letter = models.TextField('求职信', blank=True)
    
    applied_at = models.DateTimeField('投递时间', auto_now_add=True)
    viewed_at = models.DateTimeField('查看时间', null=True, blank=True)
    
    class Meta:
        db_table = 'job_applications'
        verbose_name = '简历投递'
        verbose_name_plural = '简历投递'
        unique_together = ['student', 'job_posting']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.job_posting.title}"


class JobFair(models.Model):
    """招聘会"""
    title = models.CharField('招聘会名称', max_length=200)
    description = models.TextField('描述', blank=True)
    location = models.CharField('地点', max_length=200)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    
    # 报名信息
    registration_start = models.DateTimeField('报名开始时间')
    registration_end = models.DateTimeField('报名结束时间')
    capacity = models.IntegerField('容量', default=0)
    registered_count = models.IntegerField('已报名人数', default=0)
    
    # 参与企业
    companies = models.ManyToManyField(Company, related_name='job_fairs', blank=True)
    
    is_active = models.BooleanField('是否有效', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'job_fairs'
        verbose_name = '招聘会'
        verbose_name_plural = '招聘会'
        ordering = ['-start_time']
    
    def __str__(self):
        return self.title


class JobFairRegistration(models.Model):
    """招聘会报名"""
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='job_fair_registrations',
        verbose_name='学生'
    )
    job_fair = models.ForeignKey(
        JobFair,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='招聘会'
    )
    registered_at = models.DateTimeField('报名时间', auto_now_add=True)
    
    class Meta:
        db_table = 'job_fair_registrations'
        verbose_name = '招聘会报名'
        verbose_name_plural = '招聘会报名'
        unique_together = ['student', 'job_fair']
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.job_fair.title}"


class EmploymentStatistics(models.Model):
    """就业数据统计"""
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='employment_statistics',
        verbose_name='学生'
    )
    
    # 就业信息
    is_employed = models.BooleanField('是否就业', default=False)
    employment_type = models.CharField('就业类型', max_length=50, blank=True)
    # 如：签约就业、灵活就业、自主创业、升学、出国等
    
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='就业单位'
    )
    position = models.CharField('职位', max_length=100, blank=True)
    salary = models.DecimalField('薪资', max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField('就业地点', max_length=200, blank=True)
    
    # 时间信息
    employment_date = models.DateField('就业日期', null=True, blank=True)
    graduation_year = models.CharField('毕业年份', max_length=10)
    
    # 其他信息
    major_match = models.BooleanField('专业对口', default=True)
    satisfaction = models.IntegerField('满意度', null=True, blank=True)  # 1-5分
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'employment_statistics'
        verbose_name = '就业数据'
        verbose_name_plural = '就业数据'
        unique_together = ['student', 'graduation_year']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.graduation_year}"
