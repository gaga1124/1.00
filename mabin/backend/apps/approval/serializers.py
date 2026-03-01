from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.students.serializers import StudentSerializer
from .models import LeaveApplication, ReimbursementApplication, PartyMembershipApplication
from django.conf import settings

User = get_user_model()

from apps.workflow.serializers import WorkflowInstanceSimpleSerializer
from django.contrib.contenttypes.models import ContentType
from apps.workflow.models import WorkflowInstance

class LeaveApplicationSerializer(serializers.ModelSerializer):
    """请假申请序列化器"""
    applicant_name = serializers.CharField(source='applicant.real_name', read_only=True)
    approver_name = serializers.CharField(source='approver.real_name', read_only=True)
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    applicant_type_display = serializers.CharField(source='get_applicant_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    cc_user_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    # 写入时允许以URL/路径字符串提供医疗证明；读取时提供可访问URL
    medical_certificate = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    medical_certificate_url = serializers.SerializerMethodField(read_only=True)
    cc_info = serializers.SerializerMethodField()
    workflow_instance = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'applicant', 'applicant_name', 'applicant_type', 'applicant_type_display',
            'leave_type', 'leave_type_display', 'start_time', 'end_time', 'days', 'reason',
            'medical_certificate', 'medical_certificate_url', 'attachments', 'status', 'status_display',
            'approver', 'approver_name', 'approval_comment', 'approval_time',
            'created_at', 'updated_at', 'cc_user_ids', 'cc_info', 'workflow_instance'
        ]
        read_only_fields = ['id', 'applicant', 'status', 'approver', 'approval_time', 'created_at', 'updated_at']

    def get_workflow_instance(self, obj):
        ct = ContentType.objects.get_for_model(obj.__class__)
        instance = WorkflowInstance.objects.filter(content_type=ct, object_id=obj.id).first()
        if instance:
            return WorkflowInstanceSimpleSerializer(instance).data
        return None

    def get_medical_certificate_url(self, obj):
        try:
            return obj.medical_certificate.url if obj.medical_certificate else None
        except Exception:
            return None

    def get_cc_info(self, obj):
        return [
            {
                'user_id': cc.user.id,
                'real_name': cc.user.real_name,
                'is_read': cc.is_read
            } for cc in obj.cc_records.all()
        ]

    def create(self, validated_data):
        cc_user_ids = validated_data.pop('cc_user_ids', [])
        medical_certificate_value = validated_data.pop('medical_certificate', None)
        instance = super().create(validated_data)
        
        # 处理医疗证明为URL/路径的情况（保存为FileField的name）
        if medical_certificate_value:
            # 兼容绝对URL与/media/前缀
            value = str(medical_certificate_value)
            rel_path = value
            if '://'+'' in value or value.startswith('http'):
                # 截取/media/之后的相对路径
                idx = value.find('/media/')
                if idx != -1:
                    rel_path = value[idx + len('/media/'):]
            elif value.startswith('/media/'):
                rel_path = value[len('/media/'):]
            # 直接设置文件名（Django会按Storage解析为文件路径）
            try:
                instance.medical_certificate.name = rel_path
                instance.save(update_fields=['medical_certificate'])
            except Exception:
                pass
        
        # Create CC records
        from .models import LeaveApplicationCC
        if cc_user_ids:
            users = User.objects.filter(id__in=cc_user_ids)
            for user in users:
                LeaveApplicationCC.objects.create(application=instance, user=user)
        else:
            # 自动抄送：优先抄送所在部门负责人
            try:
                dept = getattr(instance.applicant, 'department', None)
                leader = getattr(dept, 'leader', None) if dept else None
                if leader:
                    LeaveApplicationCC.objects.get_or_create(application=instance, user=leader)
            except Exception:
                pass
                
        return instance


class ReimbursementApplicationSerializer(serializers.ModelSerializer):
    """财务报销序列化器"""
    applicant_name = serializers.CharField(source='applicant.real_name', read_only=True)
    approver_name = serializers.CharField(source='approver.real_name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    cc_user_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    cc_info = serializers.SerializerMethodField()
    workflow_instance = serializers.SerializerMethodField()
    
    class Meta:
        model = ReimbursementApplication
        fields = [
            'id', 'applicant', 'applicant_name', 'title', 'category', 'category_display',
            'amount', 'reason', 'attachments', 'status', 'status_display',
            'approver', 'approver_name', 'approval_comment', 'approval_time',
            'created_at', 'updated_at', 'cc_user_ids', 'cc_info', 'workflow_instance'
        ]
        read_only_fields = ['id', 'applicant', 'status', 'approver', 'approval_time', 'created_at', 'updated_at']

    def get_workflow_instance(self, obj):
        ct = ContentType.objects.get_for_model(obj.__class__)
        instance = WorkflowInstance.objects.filter(content_type=ct, object_id=obj.id).first()
        if instance:
            return WorkflowInstanceSimpleSerializer(instance).data
        return None

    def get_cc_info(self, obj):
        return [
            {
                'user_id': cc.user.id,
                'real_name': cc.user.real_name,
                'is_read': cc.is_read
            } for cc in obj.cc_records.all()
        ]

    def create(self, validated_data):
        cc_user_ids = validated_data.pop('cc_user_ids', [])
        instance = super().create(validated_data)
        
        # Create CC records
        if cc_user_ids:
            from .models import ReimbursementApplicationCC
            users = User.objects.filter(id__in=cc_user_ids)
            for user in users:
                ReimbursementApplicationCC.objects.create(application=instance, user=user)
                
        return instance


class PartyMembershipApplicationSerializer(serializers.ModelSerializer):
    """入党/入团申请序列化器"""
    student_info = StudentSerializer(source='student', read_only=True)
    approver_name = serializers.CharField(source='approver.real_name', read_only=True)
    application_type_display = serializers.CharField(source='get_application_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # 写入时支持URL
    application_form = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    application_form_url = serializers.SerializerMethodField(read_only=True)
    workflow_instance = serializers.SerializerMethodField()
    
    class Meta:
        model = PartyMembershipApplication
        fields = [
            'id', 'student', 'student_info', 'application_type', 'application_type_display',
            'application_form', 'application_form_url', 'thought_reports', 'other_materials',
            'status', 'status_display', 'current_step',
            'approver', 'approver_name', 'approval_comment', 'approval_time',
            'created_at', 'updated_at', 'workflow_instance'
        ]
        read_only_fields = ['id', 'student', 'status', 'approver', 'approval_time', 'created_at', 'updated_at']

    def get_workflow_instance(self, obj):
        ct = ContentType.objects.get_for_model(obj.__class__)
        instance = WorkflowInstance.objects.filter(content_type=ct, object_id=obj.id).first()
        if instance:
            return WorkflowInstanceSimpleSerializer(instance).data
        return None

    def get_application_form_url(self, obj):
        try:
            return obj.application_form.url if obj.application_form else None
        except Exception:
            return None

    def create(self, validated_data):
        application_form_value = validated_data.pop('application_form', None)
        instance = super().create(validated_data)
        
        # 处理申请书为URL的情况
        if application_form_value:
            # 兼容前端传来的数组或字符串
            value = application_form_value
            if isinstance(value, list) and len(value) > 0:
                value = value[0].get('url', '')
            
            value = str(value)
            rel_path = value
            if '://' in value or value.startswith('http'):
                idx = value.find('/media/')
                if idx != -1:
                    rel_path = value[idx + len('/media/'):]
            elif value.startswith('/media/'):
                rel_path = value[len('/media/'):]
                
            try:
                instance.application_form.name = rel_path
                instance.save(update_fields=['application_form'])
            except Exception:
                pass
                
        return instance
