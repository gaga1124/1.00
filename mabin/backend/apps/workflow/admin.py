from django.contrib import admin
from .models import Workflow, WorkflowNode, WorkflowInstance, WorkflowInstanceNode


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    raw_id_fields = ['created_by']


@admin.register(WorkflowNode)
class WorkflowNodeAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'name', 'order', 'approver_type', 'is_parallel', 'is_active']
    list_filter = ['workflow', 'approver_type', 'is_parallel', 'is_active']
    search_fields = ['name', 'workflow__name']
    raw_id_fields = ['workflow', 'approver_user', 'approver_role']


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ['title', 'workflow', 'applicant', 'status', 'current_node', 'created_at']
    list_filter = ['workflow', 'status', 'created_at']
    search_fields = ['title', 'applicant__real_name', 'applicant__username']
    raw_id_fields = ['workflow', 'applicant', 'current_node']


@admin.register(WorkflowInstanceNode)
class WorkflowInstanceNodeAdmin(admin.ModelAdmin):
    list_display = ['instance', 'node', 'approver', 'status', 'approval_time', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['instance__title', 'approver__real_name']
    raw_id_fields = ['instance', 'node', 'approver']
