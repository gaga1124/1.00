from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.rbac.serializers import RoleSerializer
from .models import Workflow, WorkflowNode, WorkflowInstance, WorkflowInstanceNode


class WorkflowNodeSerializer(serializers.ModelSerializer):
    """工作流节点序列化器"""
    approver_user_name = serializers.CharField(source='approver_user.real_name', read_only=True)
    approver_role_name = serializers.CharField(source='approver_role.name', read_only=True)
    approver_type_display = serializers.CharField(source='get_approver_type_display', read_only=True)
    
    class Meta:
        model = WorkflowNode
        fields = [
            'id', 'workflow', 'name', 'order', 'approver_type', 'approver_type_display',
            'approver_user', 'approver_user_name', 'approver_role', 'approver_role_name',
            'is_parallel', 'required_approvers', 'required_materials',
            'condition_expression', 'allow_reject', 'allow_reject_to_previous',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WorkflowSerializer(serializers.ModelSerializer):
    """工作流序列化器"""
    nodes = WorkflowNodeSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.real_name', read_only=True)
    instances_count = serializers.SerializerMethodField()
    code = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'code', 'description', 'is_active',
            'created_by', 'created_by_name', 'nodes', 'instances_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_instances_count(self, obj):
        return obj.instances.count() if hasattr(obj, 'instances') else 0

    def create(self, validated_data):
        if not validated_data.get('code'):
            import time
            import random
            # 生成格式：WF + 年月日 + 时间戳后4位 + 2位随机数
            timestamp = str(int(time.time()))
            date_str = time.strftime('%Y%m%d')
            validated_data['code'] = f"WF{date_str}{timestamp[-4:]}{random.randint(10, 99)}"
        return super().create(validated_data)


class WorkflowInstanceNodeSimpleSerializer(serializers.ModelSerializer):
    """工作流实例节点简易序列化器（用于嵌套）"""
    approver_name = serializers.CharField(source='approver.real_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = WorkflowInstanceNode
        fields = ['id', 'node', 'status', 'status_display', 'approver', 'approver_name', 'approval_time', 'approval_comment']

class WorkflowInstanceSimpleSerializer(serializers.ModelSerializer):
    """工作流实例简易序列化器（用于嵌套）"""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    workflow_nodes = WorkflowNodeSerializer(source='workflow.nodes', many=True, read_only=True)
    applicant_name = serializers.CharField(source='applicant.real_name', read_only=True)
    current_node_name = serializers.CharField(source='current_node.name', read_only=True)
    current_node_detail = WorkflowNodeSerializer(source='current_node', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    node_records = WorkflowInstanceNodeSimpleSerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'workflow', 'workflow_name', 'workflow_nodes', 'title', 'description',
            'status', 'status_display', 'current_node', 'current_node_name', 'current_node_detail',
            'applicant', 'applicant_name', 'node_records', 'created_at', 'updated_at'
        ]

class WorkflowInstanceNodeSerializer(serializers.ModelSerializer):
    """工作流实例节点序列化器"""
    node_name = serializers.CharField(source='node.name', read_only=True)
    allow_reject = serializers.BooleanField(source='node.allow_reject', read_only=True)
    allow_reject_to_previous = serializers.BooleanField(source='node.allow_reject_to_previous', read_only=True)
    approver_name = serializers.CharField(source='approver.real_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    instance_detail = WorkflowInstanceSimpleSerializer(source='instance', read_only=True)
    
    class Meta:
        model = WorkflowInstanceNode
        fields = [
            'id', 'instance', 'instance_detail', 'node', 'node_name', 'allow_reject', 'allow_reject_to_previous',
            'status', 'status_display', 'approver', 'approver_name', 
            'approval_comment', 'approval_time', 'attachments', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    """工作流实例序列化器"""
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    workflow_nodes = WorkflowNodeSerializer(source='workflow.nodes', many=True, read_only=True)
    applicant_name = serializers.CharField(source='applicant.real_name', read_only=True)
    current_node_name = serializers.CharField(source='current_node.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    node_records = WorkflowInstanceNodeSerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'workflow', 'workflow_name', 'workflow_nodes', 'title', 'description',
            'status', 'status_display', 'current_node', 'current_node_name',
            'applicant', 'applicant_name', 'attachments', 'extra_data',
            'node_records', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']
