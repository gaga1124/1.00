from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class Workflow(models.Model):
    """工作流定义"""
    name = models.CharField('流程名称', max_length=100)
    code = models.CharField('流程编码', max_length=50, unique=True)
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_workflows',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'workflows'
        verbose_name = '工作流'
        verbose_name_plural = '工作流'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class WorkflowNode(models.Model):
    """工作流节点"""
    APPROVER_TYPES = [
        ('user', '指定用户'),
        ('role', '指定角色'),
        ('department_leader', '部门负责人'),
        ('creator', '创建人'),
    ]
    
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='nodes',
        verbose_name='工作流'
    )
    name = models.CharField('节点名称', max_length=100)
    order = models.IntegerField('顺序', default=0)
    
    # 审批人配置
    approver_type = models.CharField('审批人类型', max_length=20, choices=APPROVER_TYPES)
    approver_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approver_nodes',
        verbose_name='指定审批人'
    )
    approver_role = models.ForeignKey(
        'rbac.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approver_nodes',
        verbose_name='指定角色'
    )
    
    # 会签配置
    is_parallel = models.BooleanField('是否并行（会签）', default=False)
    required_approvers = models.IntegerField('需要审批人数', default=1)
    
    # 必填材料
    required_materials = models.JSONField('必填材料', default=list, blank=True)
    # 示例：[{"name": "申请书", "type": "file", "required": true}]
    
    # 条件分支
    condition_expression = models.TextField('条件表达式', blank=True)
    # 示例：amount > 10000 表示金额大于10000时走此节点
    
    # 是否允许驳回
    allow_reject = models.BooleanField('允许驳回', default=True)
    allow_reject_to_previous = models.BooleanField('允许驳回至上一步', default=True)
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'workflow_nodes'
        verbose_name = '工作流节点'
        verbose_name_plural = '工作流节点'
        ordering = ['workflow', 'order']
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name}"


class WorkflowInstance(models.Model):
    """工作流实例"""
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('processing', '审批中'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
        ('cancelled', '已取消'),
    ]
    
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name='工作流'
    )
    title = models.CharField('标题', max_length=200)
    description = models.TextField('描述', blank=True)
    
    # 关联业务对象（通用外键）
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    current_node = models.ForeignKey(
        WorkflowNode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_instances',
        verbose_name='当前节点'
    )
    
    # 申请人
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applied_workflows',
        verbose_name='申请人'
    )
    
    # 附件
    attachments = models.JSONField('附件列表', default=list, blank=True)
    
    # 扩展数据
    extra_data = models.JSONField('扩展数据', default=dict, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    
    class Meta:
        db_table = 'workflow_instances'
        verbose_name = '工作流实例'
        verbose_name_plural = '工作流实例'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # 记录旧状态
        old_status = None
        if self.pk:
            old_status = WorkflowInstance.objects.get(pk=self.pk).status
        
        super().save(*args, **kwargs)
        
        # 如果状态发生变化，且关联了业务对象，同步业务对象状态
        if self.status != old_status and self.content_object:
            try:
                # 某些业务对象可能没有 status 字段，或者字段名不同
                if hasattr(self.content_object, 'status'):
                    # 如果工作流通过，业务对象也通过
                    if self.status in ['approved', 'rejected', 'cancelled']:
                        self.content_object.status = self.status
                        # 记录审批信息（如果业务对象有对应字段）
                        if hasattr(self.content_object, 'approval_time'):
                            from django.utils import timezone
                            self.content_object.approval_time = timezone.now()
                        self.content_object.save(update_fields=['status', 'approval_time'] if hasattr(self.content_object, 'approval_time') else ['status'])
            except Exception as e:
                print(f"Error syncing workflow status to content object: {e}")

    def __str__(self):
        return f"{self.workflow.name} - {self.title}"


class WorkflowInstanceNode(models.Model):
    """工作流实例节点记录"""
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
        ('skipped', '已跳过'),
    ]
    
    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='node_records',
        verbose_name='工作流实例'
    )
    node = models.ForeignKey(
        WorkflowNode,
        on_delete=models.CASCADE,
        related_name='instance_records',
        verbose_name='节点'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 审批人
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_approvals',
        verbose_name='审批人'
    )
    approval_comment = models.TextField('审批意见', blank=True)
    approval_time = models.DateTimeField('审批时间', null=True, blank=True)
    
    # 附件
    attachments = models.JSONField('附件列表', default=list, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'workflow_instance_nodes'
        verbose_name = '工作流实例节点'
        verbose_name_plural = '工作流实例节点'
        ordering = ['instance', 'node__order']
        unique_together = ['instance', 'node', 'approver']
    
    def __str__(self):
        return f"{self.instance.title} - {self.node.name} - {self.get_status_display()}"
