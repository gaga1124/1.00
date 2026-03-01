from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LeaveApplication(models.Model):
    """请假申请"""
    LEAVE_TYPES = [
        ('sick', '病假'),
        ('personal', '事假'),
        ('business', '因公'),
        ('other', '其他'),
    ]
    
    APPLICANT_TYPES = [
        ('student', '学生'),
        ('teacher', '教职工'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已驳回'),
        ('cancelled', '已取消'),
    ]
    
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leave_applications',
        verbose_name='申请人'
    )
    applicant_type = models.CharField('申请人类型', max_length=20, choices=APPLICANT_TYPES)
    leave_type = models.CharField('请假类型', max_length=20, choices=LEAVE_TYPES)
    
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    days = models.DecimalField('请假天数', max_digits=5, decimal_places=1)
    reason = models.TextField('请假原因')
    
    # 证明材料（病假需要）
    medical_certificate = models.FileField(
        '医院证明',
        upload_to='approval/leave/',
        blank=True,
        null=True
    )
    attachments = models.JSONField('附件列表', default=list, blank=True)
    
    # 审批信息
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        verbose_name='审批人'
    )
    approval_comment = models.TextField('审批意见', blank=True)
    approval_time = models.DateTimeField('审批时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'leave_applications'
        verbose_name = '请假申请'
        verbose_name_plural = '请假申请'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.applicant.real_name} - {self.get_leave_type_display()}"

    @property
    def counselor(self):
        """用于工作流动态取审批人：学生对应的辅导员"""
        try:
            sp = getattr(self.applicant, 'student_profile', None)
            return getattr(sp, 'counselor', None)
        except Exception:
            return None


class ReimbursementApplication(models.Model):
    """财务报销申请"""
    CATEGORY_CHOICES = [
        ('office', '办公费'),
        ('travel', '差旅费'),
        ('research', '科研费'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已驳回'),
        ('cancelled', '已取消'),
        ('paid', '已支付'),
    ]
    
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reimbursement_applications',
        verbose_name='申请人'
    )
    category = models.CharField('报销类别', max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField('报销标题', max_length=200)
    description = models.TextField('描述', blank=True)
    
    # 金额
    amount = models.DecimalField('报销金额', max_digits=10, decimal_places=2)
    currency = models.CharField('币种', max_length=10, default='CNY')
    
    # 经费卡
    fund_card_number = models.CharField('经费卡号', max_length=50, blank=True)
    fund_card_balance = models.DecimalField('经费卡余额', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 发票附件
    invoices = models.JSONField('发票列表', default=list, blank=True)
    # 示例：[{"name": "发票1.pdf", "url": "/media/...", "amount": 100.00}]
    
    # 审批信息
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reimbursements',
        verbose_name='审批人'
    )
    approval_comment = models.TextField('审批意见', blank=True)
    approval_time = models.DateTimeField('审批时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'reimbursement_applications'
        verbose_name = '财务报销'
        verbose_name_plural = '财务报销'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.applicant.real_name} - {self.title} - ¥{self.amount}"


class PartyMembershipApplication(models.Model):
    """入党/入团申请"""
    APPLICATION_TYPES = [
        ('party', '入党申请'),
        ('league', '入团申请'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已驳回'),
        ('cancelled', '已取消'),
    ]
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='party_applications',
        verbose_name='学生'
    )
    application_type = models.CharField('申请类型', max_length=20, choices=APPLICATION_TYPES)
    
    # 申请材料
    application_form = models.FileField('申请书', upload_to='approval/party/', blank=True, null=True)
    thought_reports = models.JSONField('思想汇报列表', default=list, blank=True)
    other_materials = models.JSONField('其他材料', default=list, blank=True)
    
    # 审批信息
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    current_step = models.CharField('当前步骤', max_length=50, blank=True)
    
    # 审批人
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_party_applications',
        verbose_name='审批人'
    )
    approval_comment = models.TextField('审批意见', blank=True)
    approval_time = models.DateTimeField('审批时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'party_membership_applications'
        verbose_name = '入党/入团申请'
        verbose_name_plural = '入党/入团申请'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.get_application_type_display()}"


class LeaveApplicationCC(models.Model):
    """请假申请抄送记录"""
    application = models.ForeignKey(LeaveApplication, on_delete=models.CASCADE, related_name='cc_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_cc_records')
    is_read = models.BooleanField('已阅', default=False)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '请假抄送'
        verbose_name_plural = verbose_name
        unique_together = ['application', 'user']

class ReimbursementApplicationCC(models.Model):
    """报销申请抄送记录"""
    application = models.ForeignKey(ReimbursementApplication, on_delete=models.CASCADE, related_name='cc_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reimbursement_cc_records')
    is_read = models.BooleanField('已阅', default=False)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '报销抄送'
        verbose_name_plural = verbose_name
        unique_together = ['application', 'user']
