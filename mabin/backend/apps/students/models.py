from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Student(models.Model):
    """学生基础档案"""
    POLITICAL_STATUS_CHOICES = [
        ('masses', '群众'),
        ('member', '团员'),
        ('activist', '入党积极分子'),
        ('probationary', '预备党员'),
        ('party_member', '正式党员'),
    ]
    
    # 基础信息
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='用户'
    )
    student_id = models.CharField('学号', max_length=50, unique=True)
    major = models.CharField('专业', max_length=100)
    class_name = models.CharField('班级', max_length=50)
    grade = models.CharField('年级', max_length=10)  # 如：2021级
    # 所在学院/部门（关键：学院归属）
    department = models.ForeignKey(
        'rbac.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='学院/部门'
    )
    # 对应辅导员（关键：一对一的学生-辅导员关系）
    counselor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='counseling_students',
        verbose_name='辅导员'
    )
    
    # 政治面貌
    political_status = models.CharField(
        '政治面貌',
        max_length=20,
        choices=POLITICAL_STATUS_CHOICES,
        default='masses'
    )
    
    # 照片
    photo = models.ImageField('照片', upload_to='students/photos/', blank=True, null=True)
    
    # 扩展信息（JSON存储）
    extra_data = models.JSONField('扩展数据', default=dict, blank=True)
    # 示例结构：
    # {
    #   "awards": [...],  # 获奖记录
    #   "punishments": [...],  # 惩处记录
    #   "research": [...],  # 科研成果
    #   "poverty_identification": {...},  # 贫困生认定
    # }
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'students'
        verbose_name = '学生档案'
        verbose_name_plural = '学生档案'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.real_name} ({self.student_id})"


class PoliticalStatusRecord(models.Model):
    """政治面貌流转记录"""
    STATUS_CHOICES = [
        ('masses', '群众'),
        ('member', '团员'),
        ('activist', '入党积极分子'),
        ('probationary', '预备党员'),
        ('party_member', '正式党员'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='political_status_records',
        verbose_name='学生'
    )
    from_status = models.CharField('原状态', max_length=20, choices=STATUS_CHOICES)
    to_status = models.CharField('目标状态', max_length=20, choices=STATUS_CHOICES)
    application_date = models.DateField('申请日期')
    approval_date = models.DateField('批准日期', null=True, blank=True)
    status = models.CharField(
        '审批状态',
        max_length=20,
        choices=[
            ('pending', '待审批'),
            ('approved', '已批准'),
            ('rejected', '已驳回'),
        ],
        default='pending'
    )
    
    # 相关材料
    application_file = models.FileField(
        '申请书',
        upload_to='students/political/',
        blank=True,
        null=True
    )
    thought_report = models.FileField(
        '思想汇报',
        upload_to='students/political/',
        blank=True,
        null=True
    )
    other_materials = models.JSONField('其他材料', default=list, blank=True)
    
    # 审批信息
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='political_approvals',
        verbose_name='审批人'
    )
    approval_comment = models.TextField('审批意见', blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'political_status_records'
        verbose_name = '政治面貌流转记录'
        verbose_name_plural = '政治面貌流转记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.get_from_status_display()} -> {self.get_to_status_display()}"


class StudentRecord(models.Model):
    """学生档案记录（动态扩展）"""
    RECORD_TYPES = [
        ('award', '获奖记录'),
        ('punishment', '惩处记录'),
        ('research', '科研成果'),
        ('poverty', '贫困生认定'),
        ('activity', '活动参与'),
        ('other', '其他'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='学生'
    )
    record_type = models.CharField('记录类型', max_length=20, choices=RECORD_TYPES)
    title = models.CharField('标题', max_length=200)
    description = models.TextField('描述', blank=True)
    
    # 记录数据（JSON）
    record_data = models.JSONField('记录数据', default=dict, blank=True)
    
    # 附件
    attachments = models.JSONField('附件列表', default=list, blank=True)
    # 示例：[{"name": "证书.pdf", "url": "/media/...", "size": 1024}]
    
    # 操作信息
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='student_records_created',
        verbose_name='操作人'
    )
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'student_records'
        verbose_name = '学生档案记录'
        verbose_name_plural = '学生档案记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.get_record_type_display()} - {self.title}"


class StudentStatusChange(models.Model):
    """学籍变动记录"""
    CHANGE_TYPES = [
        ('enrolled', '入学'),
        ('transfer_in', '转入'),
        ('transfer_out', '转出'),
        ('suspend', '休学'),
        ('resume', '复学'),
        ('withdraw', '退学'),
        ('graduate', '毕业'),
        ('other', '其他'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='status_changes',
        verbose_name='学生'
    )
    change_type = models.CharField('变动类型', max_length=20, choices=CHANGE_TYPES)
    from_status = models.CharField('变动前状态', max_length=50, blank=True)
    to_status = models.CharField('变动后状态', max_length=50)
    reason = models.TextField('变动原因')
    change_date = models.DateField('变动日期')
    
    # 证明文件
    document_no = models.CharField('文件编号', max_length=100, blank=True)
    attachments = models.JSONField('附件列表', default=list, blank=True)
    
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='student_status_changes',
        verbose_name='经办人'
    )
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'student_status_changes'
        verbose_name = '学籍变动记录'
        verbose_name_plural = '学籍变动记录'
        ordering = ['-change_date', '-created_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.get_change_type_display()}"


class ArchiveViewLog(models.Model):
    """档案查阅日志"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='view_logs',
        verbose_name='被查阅学生'
    )
    viewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_view_history',
        verbose_name='查阅人'
    )
    reason = models.CharField('查阅原因', max_length=200, blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    viewed_at = models.DateTimeField('查阅时间', auto_now_add=True)

    class Meta:
        db_table = 'archive_view_logs'
        verbose_name = '档案查阅日志'
        verbose_name_plural = verbose_name
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.viewer.real_name} 查阅了 {self.student.user.real_name} 的档案"
