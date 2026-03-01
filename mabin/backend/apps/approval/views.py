from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from .models import (
    LeaveApplication, ReimbursementApplication, PartyMembershipApplication,
    LeaveApplicationCC, ReimbursementApplicationCC
)
from .serializers import (
    LeaveApplicationSerializer, ReimbursementApplicationSerializer,
    PartyMembershipApplicationSerializer
)
from apps.workflow.models import Workflow, WorkflowNode, WorkflowInstance, WorkflowInstanceNode
from apps.rbac.models import Role
from decimal import Decimal


from apps.workflow.models import Workflow, WorkflowNode, WorkflowInstance, WorkflowInstanceNode

class WorkflowAwareApprovalMixin:
    """支持工作流的审批 Mixin"""
    def _handle_approve(self, application, request):
        action_type = request.data.get('action')
        comment = request.data.get('comment', '')
        
        # 查找关联的工作流实例
        ct = ContentType.objects.get_for_model(application.__class__)
        wi = WorkflowInstance.objects.filter(content_type=ct, object_id=application.id).first()
        
        if wi and wi.status in ['pending', 'processing']:
            # 如果存在工作流且正在处理中，调用工作流审批逻辑
            from apps.workflow.views import WorkflowInstanceViewSet
            helper = WorkflowInstanceViewSet()
            helper.request = request
            
            # 这里的逻辑需要模拟 WorkflowInstanceViewSet.approve
            node_record = WorkflowInstanceNode.objects.filter(
                instance=wi,
                node=wi.current_node,
                approver=request.user,
                status='pending'
            ).first()
            
            if not node_record:
                # 兼容性：如果不是当前节点的直接审批人，但具有管理员权限或特定权限，也可以简单处理
                # 但推荐通过 WorkflowInstance 直接处理。这里为了简化，若找不到记录则返回 403
                return Response({'error': '您当前没有审批权限或已审批'}, status=403)
            
            # 模拟 WorkflowInstanceViewSet.approve 的核心逻辑
            if action_type == 'approve':
                node_record.status = 'approved'
                node_record.approval_comment = comment
                node_record.approval_time = timezone.now()
                node_record.save()
                
                # 检查会签
                if wi.current_node.is_parallel:
                    approved_count = WorkflowInstanceNode.objects.filter(
                        instance=wi, node=wi.current_node, status='approved'
                    ).count()
                    if approved_count < wi.current_node.required_approvers:
                        return Response({'message': '审批已提交，等待其他审批人'})
                
                helper._move_to_next_node(wi)
            elif action_type == 'reject':
                node_record.status = 'rejected'
                node_record.approval_comment = comment
                node_record.approval_time = timezone.now()
                node_record.save()
                wi.status = 'rejected'
                wi.completed_at = timezone.now()
                wi.save()
            elif action_type == 'reject_to_previous':
                # 驳回至上一步
                current_order = wi.current_node.order
                previous_node = wi.workflow.nodes.filter(is_active=True, order__lt=current_order).order_by('-order').first()
                if not previous_node:
                    return Response({'error': '已经是第一个节点，无法驳回至上一步'}, status=400)
                node_record.status = 'rejected'
                node_record.approval_comment = comment
                node_record.approval_time = timezone.now()
                node_record.save()
                wi.current_node = previous_node
                wi.status = 'processing'
                wi.save()
                helper._create_node_records(wi, previous_node)
            
            # 状态同步已由 WorkflowInstance.save 处理
            application.refresh_from_db()
        else:
            # 无工作流，走简单直接审批逻辑
            if action_type == 'approve':
                application.status = 'approved'
                application.approval_time = timezone.now()
            elif action_type == 'reject':
                application.status = 'rejected'
            else:
                return Response({'error': '无效的操作类型'}, status=400)
            
            application.approver = request.user
            application.approval_comment = comment
            application.save()
            
        return Response(self.get_serializer(application).data)

class LeaveApplicationViewSet(WorkflowAwareApprovalMixin, viewsets.ModelViewSet):
    """请假申请视图集"""
    queryset = LeaveApplication.objects.all()
    serializer_class = LeaveApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据用户角色过滤"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        # 返回自己申请的、需要自己审批的、或者是抄送给自己的
        return queryset.filter(
            Q(applicant=user) |
            Q(approver=user, status='pending') |
            Q(cc_records__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        application = serializer.save(applicant=self.request.user)
        # 自动识别申请人类型
        try:
            application.applicant_type = 'student' if application.applicant.has_role('student') else 'teacher'
            application.save(update_fields=['applicant_type'])
        except Exception:
            pass
        # 确保请假流程存在并创建实例
        workflow = self._ensure_leave_workflow()
        self._attach_workflow_instance(
            workflow=workflow,
            applicant=application.applicant,
            title=f"学生请假 - {application.applicant.real_name} - {application.days}天",
            content_obj=application
        )
    
    def _ensure_leave_workflow(self):
        """确保学生请假流程存在：辅导员 -> (days>3)学院书记 -> (days>14)学生工作处"""
        wf, _ = Workflow.objects.get_or_create(
            code='WF_LEAVE_STUDENT',
            defaults={'name': '学生请假流程', 'description': '按请假天数增加审批层级', 'created_by': self.request.user}
        )
        # 角色准备
        counselor_role = Role.objects.filter(code='counselor').first() or Role.objects.create(name='辅导员', code='counselor', role_type='counselor', is_system=True)
        student_affairs = Role.objects.filter(code='student_affairs').first()
        if not student_affairs:
            student_affairs = Role.objects.create(name='学生工作处', code='student_affairs', role_type='leader', is_system=True)
        # 节点同步（幂等创建）
        node_defs = [
            # 第一节点：直接指定学生的辅导员（通过 approver_field:counselor 从业务对象获取）
            {'order': 1, 'name': '辅导员审批', 'approver_type': 'user', 'approver_role': None, 'condition_expression': 'approver_field:counselor'},
            {'order': 2, 'name': '学院书记审批', 'approver_type': 'department_leader', 'approver_role': None, 'condition_expression': 'days > 3'},
            {'order': 3, 'name': '学生工作处审批', 'approver_type': 'role', 'approver_role': student_affairs, 'condition_expression': 'days > 14'},
        ]
        for nd in node_defs:
            node, created = WorkflowNode.objects.get_or_create(
                workflow=wf, order=nd['order'],
                defaults={
                    'name': nd['name'],
                    'approver_type': nd['approver_type'],
                    'approver_role': nd['approver_role'],
                    'approver_user': None,
                    'condition_expression': nd['condition_expression'],
                    'is_active': True
                }
            )
            # 若已存在但需要更新关键字段，做同步
            updated = False
            if node.name != nd['name']:
                node.name = nd['name']; pipeline=True; updated=True
            if node.approver_type != nd['approver_type']:
                node.approver_type = nd['approver_type']; updated=True
            if node.approver_role_id != (nd['approver_role'].id if nd['approver_role'] else None):
                node.approver_role = nd['approver_role']; updated=True
            if (node.condition_expression or '') != nd['condition_expression']:
                node.condition_expression = nd['condition_expression']; updated=True
            if updated:
                node.save()
        return wf
    
    def _attach_workflow_instance(self, workflow, applicant, title, content_obj):
        """创建并初始化工作流实例，自动跳过不匹配节点"""
        instance = WorkflowInstance.objects.create(
            workflow=workflow,
            title=title,
            applicant=applicant,
            status='pending',
            content_type=ContentType.objects.get_for_model(content_obj.__class__),
            object_id=content_obj.id
        )
        # 初始化首个匹配节点
        from apps.workflow.views import WorkflowInstanceViewSet  # 复用已实现的逻辑
        helper = WorkflowInstanceViewSet()
        helper.request = self.request  # 为了权限上下文一致
        # 寻找第一匹配节点（from_order=0）
        first_node = helper._find_next_matching_node(instance, from_order=0)
        if not first_node:
            # 无需审批，直接通过
            instance.status = 'approved'
            instance.save()
            return instance
        instance.current_node = first_node
        instance.status = 'processing'
        instance.save()
        if not helper._create_node_records(instance, first_node):
            helper._auto_skip_node(instance, first_node)
            helper._move_to_next_node(instance)
        return instance
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批请假"""
        application = self.get_object()
        return self._handle_approve(application, request)

    @action(detail=True, methods=['post'])
    def mark_cc_read(self, request, pk=None):
        """标记抄送已阅"""
        application = self.get_object()
        user = request.user
        
        try:
            cc_record = LeaveApplicationCC.objects.get(application=application, user=user)
            cc_record.is_read = True
            cc_record.read_at = timezone.now()
            cc_record.save()
            return Response({'status': 'success'})
        except LeaveApplicationCC.DoesNotExist:
            return Response({'error': '未找到抄送记录'}, status=404)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        application = self.get_object()
        if application.applicant != request.user and not request.user.is_superuser:
            return Response({'error': '无权撤回该申请'}, status=403)
        if application.status in ['approved', 'rejected', 'cancelled']:
            return Response({'error': '当前状态不可撤回'}, status=400)
        application.status = 'cancelled'
        application.approval_comment = '申请人撤回'
        application.approval_time = timezone.now()
        application.save()
        try:
            ct = ContentType.objects.get_for_model(LeaveApplication)
            wi = WorkflowInstance.objects.filter(content_type=ct, object_id=application.id).first()
            if wi and wi.status in ['pending', 'processing']:
                wi.status = 'cancelled'
                wi.current_node = None
                wi.completed_at = timezone.now()
                wi.save()
        except Exception:
            pass
        return Response(self.get_serializer(application).data)


class ReimbursementApplicationViewSet(WorkflowAwareApprovalMixin, viewsets.ModelViewSet):
    """财务报销视图集"""
    queryset = ReimbursementApplication.objects.all()
    serializer_class = ReimbursementApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据用户角色过滤"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser or getattr(user, 'has_role', None) and (user.has_role('finance') or user.has_role('finance_director')):
            return queryset
        
        return queryset.filter(
            Q(applicant=user) |
            Q(approver=user, status='pending') |
            Q(cc_records__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        application = serializer.save(applicant=self.request.user)
        # 确保报销流程存在并创建实例
        workflow = self._ensure_reimbursement_workflow()
        self._attach_workflow_instance(
            workflow=workflow,
            applicant=application.applicant,
            title=f"财务报销 - {application.applicant.real_name} - ¥{application.amount}",
            content_obj=application
        )
    
    def _ensure_reimbursement_workflow(self):
        """确保报销流程存在：学院主管领导 -> 财务处审批 -> (amount>=10000)财务处负责人"""
        wf, _ = Workflow.objects.get_or_create(
            code='WF_REIMBURSEMENT_TEACHER',
            defaults={'name': '财务报销流程', 'description': '按报销金额动态增加审批层级', 'created_by': self.request.user}
        )
        # 角色准备
        finance = Role.objects.filter(code='finance').first()
        if not finance:
            finance = Role.objects.create(name='财务处', code='finance', role_type='leader', is_system=True)
        finance_director = Role.objects.filter(code='finance_director').first()
        if not finance_director:
            finance_director = Role.objects.create(name='财务处负责人', code='finance_director', role_type='leader', is_system=True)
        # 节点同步
        node_defs = [
            {'order': 1, 'name': '学院主管领导审批', 'approver_type': 'department_leader', 'approver_role': None, 'condition_expression': ''},
            {'order': 2, 'name': '财务处审批', 'approver_type': 'role', 'approver_role': finance, 'condition_expression': ''},
            {'order': 3, 'name': '财务处负责人复核', 'approver_type': 'role', 'approver_role': finance_director, 'condition_expression': 'amount >= 10000'},
        ]
        for nd in node_defs:
            node, created = WorkflowNode.objects.get_or_create(
                workflow=wf, order=nd['order'],
                defaults={
                    'name': nd['name'],
                    'approver_type': nd['approver_type'],
                    'approver_role': nd['approver_role'],
                    'approver_user': None,
                    'condition_expression': nd['condition_expression'],
                    'is_active': True
                }
            )
            updated = False
            if node.name != nd['name']:
                node.name = nd['name']; updated=True
            if node.approver_type != nd['approver_type']:
                node.approver_type = nd['approver_type']; updated=True
            if node.approver_role_id != (nd['approver_role'].id if nd['approver_role'] else None):
                node.approver_role = nd['approver_role']; updated=True
            if (node.condition_expression or '') != nd['condition_expression']:
                node.condition_expression = nd['condition_expression']; updated=True
            if updated:
                node.save()
        return wf
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批报销"""
        application = self.get_object()
        return self._handle_approve(application, request)

    @action(detail=True, methods=['post'])
    def mark_cc_read(self, request, pk=None):
        """标记抄送已阅"""
        application = self.get_object()
        user = request.user
        
        try:
            cc_record = ReimbursementApplicationCC.objects.get(application=application, user=user)
            cc_record.is_read = True
            cc_record.read_at = timezone.now()
            cc_record.save()
            return Response({'status': 'success'})
        except ReimbursementApplicationCC.DoesNotExist:
            return Response({'error': '未找到抄送记录'}, status=404)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        application = self.get_object()
        if application.applicant != request.user and not request.user.is_superuser:
            return Response({'error': '无权撤回该申请'}, status=403)
        if application.status in ['approved', 'rejected', 'cancelled', 'paid']:
            return Response({'error': '当前状态不可撤回'}, status=400)
        application.status = 'cancelled'
        application.approval_comment = '申请人撤回'
        application.approval_time = timezone.now()
        application.save()
        try:
            ct = ContentType.objects.get_for_model(ReimbursementApplication)
            wi = WorkflowInstance.objects.filter(content_type=ct, object_id=application.id).first()
            if wi and wi.status in ['pending', 'processing']:
                wi.status = 'cancelled'
                wi.current_node = None
                wi.completed_at = timezone.now()
                wi.save()
        except Exception:
            pass
        return Response(self.get_serializer(application).data)


class PartyMembershipApplicationViewSet(WorkflowAwareApprovalMixin, viewsets.ModelViewSet):
    """入党/入团申请视图集"""
    queryset = PartyMembershipApplication.objects.all()
    serializer_class = PartyMembershipApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_superuser:
            return queryset
        
        # 学生查看自己的，老师查看需要自己审批的
        if hasattr(user, 'student_profile'):
            return queryset.filter(student=user.student_profile)
        
        return queryset.filter(approver=user, status='pending')

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'student_profile'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError('只有学生可以发起入党/入团申请')
        
        application = serializer.save(student=user.student_profile, current_step='提交申请')
        
        # 触发工作流
        workflow = self._ensure_party_workflow(application.application_type)
        self._attach_workflow_instance(
            workflow=workflow,
            applicant=user,
            title=f"{application.get_application_type_display()} - {user.real_name}",
            content_obj=application
        )

    def _ensure_party_workflow(self, app_type):
        """确保入党/入团流程存在：辅导员 -> 学院书记"""
        code = f'WF_{app_type.upper()}_APPLICATION'
        name = '入党申请流程' if app_type == 'party' else '入团申请流程'
        
        wf, _ = Workflow.objects.get_or_create(
            code=code,
            defaults={'name': name, 'description': f'学生{name}', 'created_by': self.request.user}
        )
        
        # 节点同步
        node_defs = [
            {'order': 1, 'name': '辅导员初审', 'approver_type': 'user', 'approver_role': None, 'condition_expression': 'approver_field:counselor'},
            {'order': 2, 'name': '学院党委/团委审批', 'approver_type': 'department_leader', 'approver_role': None, 'condition_expression': ''},
        ]
        for nd in node_defs:
            WorkflowNode.objects.get_or_create(
                workflow=wf, order=nd['order'],
                defaults={
                    'name': nd['name'],
                    'approver_type': nd['approver_type'],
                    'approver_role': nd['approver_role'],
                    'condition_expression': nd['condition_expression'],
                    'is_active': True
                }
            )
        return wf

    def _attach_workflow_instance(self, workflow, applicant, title, content_obj):
        """创建并初始化工作流实例（复用逻辑）"""
        from apps.workflow.views import WorkflowInstanceViewSet
        instance = WorkflowInstance.objects.create(
            workflow=workflow,
            title=title,
            applicant=applicant,
            status='pending',
            content_type=ContentType.objects.get_for_model(content_obj.__class__),
            object_id=content_obj.id
        )
        helper = WorkflowInstanceViewSet()
        helper.request = self.request
        first_node = helper._find_next_matching_node(instance, from_order=0)
        if not first_node:
            instance.status = 'approved'
            instance.save()
            return instance
        instance.current_node = first_node
        instance.status = 'processing'
        instance.save()
        if not helper._create_node_records(instance, first_node):
            helper._auto_skip_node(instance, first_node)
            helper._move_to_next_node(instance)
        return instance

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批入党/入团申请"""
        application = self.get_object()
        # 对于入党申请，审批时可能需要更新 current_step
        next_step = request.data.get('next_step')
        if next_step:
            application.current_step = next_step
            application.save(update_fields=['current_step'])
            
        return self._handle_approve(application, request)
