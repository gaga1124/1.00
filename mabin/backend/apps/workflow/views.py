from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import models
from .models import Workflow, WorkflowNode, WorkflowInstance, WorkflowInstanceNode
from .serializers import (
    WorkflowSerializer, WorkflowNodeSerializer,
    WorkflowInstanceSerializer, WorkflowInstanceNodeSerializer
)
from decimal import Decimal


class WorkflowViewSet(viewsets.ModelViewSet):
    """工作流视图集"""
    queryset = Workflow.objects.filter(is_active=True)
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def create_instance(self, request, pk=None):
        """创建工作流实例"""
        workflow = self.get_object()
        serializer = WorkflowInstanceSerializer(data={
            **request.data,
            'workflow': workflow.id,
            'applicant': request.user.id,
            'status': 'pending'
        })
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # 初始化第一个匹配的节点（按条件表达式跳过不匹配节点）
        first_node = self._find_next_matching_node(instance, from_order=0)
        if first_node:
            instance.current_node = first_node
            instance.status = 'processing'
            instance.save()
            # 若无审批人则自动跳过并继续寻找下一个
            if not self._create_node_records(instance, first_node):
                self._auto_skip_node(instance, first_node)
                self._move_to_next_node(instance)
        
        return Response(WorkflowInstanceSerializer(instance).data, status=201)
    
    def _create_node_records(self, instance, node):
        """创建或重置节点审批记录。返回是否创建了至少一条待审批记录。"""
        approvers = self._get_node_approvers(instance, node)
        created_any = False
        for approver in approvers:
            WorkflowInstanceNode.objects.update_or_create(
                instance=instance,
                node=node,
                approver=approver,
                defaults={
                    'status': 'pending',
                    'approval_time': None,
                    'approval_comment': ''
                }
            )
            created_any = True
        return created_any
    
    def _get_node_approvers(self, instance, node):
        """获取节点审批人列表"""
        approvers = []
        
        if node.approver_type == 'user':
            # 兼容：若未指定固定用户，但在条件表达式中以 "approver_field:advisor" 声明，则从业务对象字段取审批人
            if node.approver_user:
                approvers.append(node.approver_user)
            elif node.condition_expression and node.condition_expression.strip().startswith('approver_field:'):
                field = node.condition_expression.strip().split(':', 1)[1].strip()
                content_obj = getattr(instance, 'content_object', None)
                if content_obj is not None and hasattr(content_obj, field):
                    candidate = getattr(content_obj, field)
                    if candidate:
                        approvers.append(candidate)
        elif node.approver_type == 'role' and node.approver_role:
            # 获取该角色的所有用户
            from apps.rbac.models import UserRole
            user_roles = UserRole.objects.filter(role=node.approver_role)
            approvers = [ur.user for ur in user_roles]
        elif node.approver_type == 'department_leader':
            if instance.applicant.department and instance.applicant.department.leader:
                approvers.append(instance.applicant.department.leader)
        elif node.approver_type == 'creator':
            approvers.append(instance.applicant)
        
        return approvers
    
    def _evaluate_condition(self, instance, node):
        """评估节点条件表达式，支持变量：days、amount、category、applicant_role。
        空表达式视为True"""
        expr = (node.condition_expression or '').strip()
        if not expr or expr.startswith('approver_field:'):
            return True
        
        content_obj = getattr(instance, 'content_object', None)
        ctx = {}
        if content_obj is not None:
            # 请假单
            if hasattr(content_obj, 'days'):
                try:
                    ctx['days'] = float(content_obj.days) if isinstance(content_obj.days, (int, float, Decimal)) else float(str(content_obj.days))
                except Exception:
                    ctx['days'] = 0.0
            # 报销
            if hasattr(content_obj, 'amount'):
                try:
                    ctx['amount'] = float(content_obj.amount)
                except Exception:
                    ctx['amount'] = 0.0
            if hasattr(content_obj, 'category'):
                ctx['category'] = getattr(content_obj, 'category')
        # 申请人角色
        try:
            roles = set(getattr(instance.applicant, 'roles', []))
        except Exception:
            roles = set()
        ctx['applicant_role'] = next(iter(roles), '')
        
        try:
            return bool(eval(expr, {'__builtins__': {}}, ctx))
        except Exception:
            # 表达式异常时安全回退为False，避免误闯关
            return False
    
    def _find_next_matching_node(self, instance, from_order):
        """从指定顺序之后查找首个满足条件的节点"""
        candidates = instance.workflow.nodes.filter(is_active=True, order__gt=from_order).order_by('order')
        for node in candidates:
            if self._evaluate_condition(instance, node):
                return node
        return None
    
    def _auto_skip_node(self, instance, node):
        """创建一条跳过记录，便于审计"""
        WorkflowInstanceNode.objects.get_or_create(
            instance=instance,
            node=node,
            approver=None,
            defaults={
                'status': 'skipped',
                'approval_time': None,
                'approval_comment': '条件不匹配或无审批人，系统自动跳过'
            }
        )


class WorkflowNodeViewSet(viewsets.ModelViewSet):
    """工作流节点视图集"""
    queryset = WorkflowNode.objects.all()
    serializer_class = WorkflowNodeSerializer
    permission_classes = [IsAuthenticated]


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    """工作流实例视图集"""
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [IsAuthenticated]
    from decimal import Decimal
    
    def get_queryset(self):
        """根据用户角色过滤"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # 如果是超级管理员，返回所有
        if user.is_superuser:
            return queryset
        
        # 否则只返回自己申请的或需要自己审批的
        return queryset.filter(
            models.Q(applicant=user) |
            models.Q(node_records__approver=user, node_records__status='pending')
        ).distinct()
    
    @action(detail=False, methods=['get'])
    def my_todos(self, request):
        """获取我的待办任务"""
        user = request.user
        todos = WorkflowInstanceNode.objects.filter(
            approver=user,
            status='pending',
            instance__status='processing'
        )
        serializer = WorkflowInstanceNodeSerializer(todos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批工作流实例"""
        instance = self.get_object()
        action_type = request.data.get('action')  # 'approve', 'reject', 'reject_to_previous'
        comment = request.data.get('comment', '')
        
        # 获取当前用户的审批节点记录
        node_record = WorkflowInstanceNode.objects.filter(
            instance=instance,
            node=instance.current_node,
            approver=request.user,
            status='pending'
        ).first()
        
        if not node_record:
            return Response({'error': '无权审批此节点'}, status=403)
        
        if action_type == 'approve':
            node_record.status = 'approved'
            node_record.approval_comment = comment
            node_record.approval_time = timezone.now()
            node_record.save()
            
            # 检查是否所有审批人都已通过（如果是会签）
            if instance.current_node.is_parallel:
                approved_count = WorkflowInstanceNode.objects.filter(
                    instance=instance,
                    node=instance.current_node,
                    status='approved'
                ).count()
                
                if approved_count < instance.current_node.required_approvers:
                    return Response({'message': '审批已提交，等待其他审批人'})
            
            # 移动到下一个节点
            self._move_to_next_node(instance)
            
        elif action_type == 'reject':
            if not instance.current_node.allow_reject:
                return Response({'error': '此节点不允许驳回'}, status=400)
            
            node_record.status = 'rejected'
            node_record.approval_comment = comment
            node_record.approval_time = timezone.now()
            node_record.save()
            
            instance.status = 'rejected'
            instance.completed_at = timezone.now()
            instance.save()
            
        elif action_type == 'reject_to_previous':
            if not instance.current_node.allow_reject_to_previous:
                return Response({'error': '此节点不允许驳回至上一步'}, status=400)
            
            # 获取上一个节点
            current_order = instance.current_node.order
            previous_node = instance.workflow.nodes.filter(
                is_active=True,
                order__lt=current_order
            ).order_by('-order').first()
            
            if not previous_node:
                return Response({'error': '已经是第一个节点，无法驳回至上一步'}, status=400)
            
            # 更新当前节点状态为已驳回
            node_record.status = 'rejected'
            node_record.approval_comment = comment
            node_record.approval_time = timezone.now()
            node_record.save()
            
            # 移动实例到上一个节点
            instance.current_node = previous_node
            instance.status = 'processing'
            instance.save()
            
            # 重置上一个节点的审批记录
            self._create_node_records(instance, previous_node)
            
            return Response(self.get_serializer(instance).data)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def _move_to_next_node(self, instance):
        """移动到下一个节点（自动评估条件并跳过不满足的节点或无审批人的节点）"""
        current_node = instance.current_node
        order_base = current_node.order if current_node else 0
        while True:
            next_node = self._find_next_matching_node(instance, from_order=order_base)
            if not next_node:
                instance.status = 'approved'
                instance.completed_at = timezone.now()
                instance.current_node = None
                instance.save()
                break
            # 切换至该节点
            instance.current_node = next_node
            instance.status = 'processing'
            instance.save()
            # 创建记录；若无审批人则跳过继续寻找
            if self._create_node_records(instance, next_node):
                break
            self._auto_skip_node(instance, next_node)
            order_base = next_node.order
    
    def _create_node_records(self, instance, node):
        """创建或重置节点审批记录。返回是否创建了至少一条待审批记录。"""
        approvers = self._get_node_approvers(instance, node)
        created_any = False
        for approver in approvers:
            WorkflowInstanceNode.objects.update_or_create(
                instance=instance,
                node=node,
                approver=approver,
                defaults={
                    'status': 'pending',
                    'approval_time': None,
                    'approval_comment': ''
                }
            )
            created_any = True
        return created_any
    
    def _get_node_approvers(self, instance, node):
        """获取节点审批人列表"""
        approvers = []
        
        if node.approver_type == 'user':
            if node.approver_user:
                approvers.append(node.approver_user)
            elif node.condition_expression and node.condition_expression.strip().startswith('approver_field:'):
                field = node.condition_expression.strip().split(':', 1)[1].strip()
                content_obj = getattr(instance, 'content_object', None)
                if content_obj is not None and hasattr(content_obj, field):
                    candidate = getattr(content_obj, field)
                    if candidate:
                        approvers.append(candidate)
        elif node.approver_type == 'role' and node.approver_role:
            # 获取该角色的所有用户
            from apps.rbac.models import UserRole
            user_roles = UserRole.objects.filter(role=node.approver_role)
            approvers = [ur.user for ur in user_roles]
        elif node.approver_type == 'department_leader':
            if instance.applicant.department and instance.applicant.department.leader:
                approvers.append(instance.applicant.department.leader)
        elif node.approver_type == 'creator':
            approvers.append(instance.applicant)
        
        return approvers
    
    def _evaluate_condition(self, instance, node):
        """评估节点条件表达式，支持变量：days、amount、category、applicant_role。空表达式视为True"""
        expr = (node.condition_expression or '').strip()
        if not expr or expr.startswith('approver_field:'):
            return True
        content_obj = getattr(instance, 'content_object', None)
        ctx = {}
        if content_obj is not None:
            if hasattr(content_obj, 'days'):
                try:
                    ctx['days'] = float(content_obj.days) if isinstance(content_obj.days, (int, float, Decimal)) else float(str(content_obj.days))
                except Exception:
                    ctx['days'] = 0.0
            if hasattr(content_obj, 'amount'):
                try:
                    ctx['amount'] = float(content_obj.amount)
                except Exception:
                    ctx['amount'] = 0.0
            if hasattr(content_obj, 'category'):
                ctx['category'] = getattr(content_obj, 'category')
        try:
            roles = set(getattr(instance.applicant, 'roles', []))
        except Exception:
            roles = set()
        ctx['applicant_role'] = next(iter(roles), '')
        try:
            return bool(eval(expr, {'__builtins__': {}}, ctx))
        except Exception:
            return False
    
    def _find_next_matching_node(self, instance, from_order):
        """从指定顺序之后查找首个满足条件的节点"""
        candidates = instance.workflow.nodes.filter(is_active=True, order__gt=from_order).order_by('order')
        for node in candidates:
            if self._evaluate_condition(instance, node):
                return node
        return None
    
    def _auto_skip_node(self, instance, node):
        """创建一条跳过记录，便于审计"""
        WorkflowInstanceNode.objects.get_or_create(
            instance=instance,
            node=node,
            approver=None,
            defaults={
                'status': 'skipped',
                'approval_time': None,
                'approval_comment': '条件不匹配或无审批人，系统自动跳过'
            }
        )


class WorkflowInstanceNodeViewSet(viewsets.ReadOnlyModelViewSet):
    """工作流实例节点视图集（只读）"""
    queryset = WorkflowInstanceNode.objects.all()
    serializer_class = WorkflowInstanceNodeSerializer
    permission_classes = [IsAuthenticated]
