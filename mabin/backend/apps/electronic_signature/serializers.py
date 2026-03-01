"""
电子签章模块序列化器
"""

from rest_framework import serializers
from .models import ElectronicFile, DepartmentSignature, FileRecipient, SignatureOperationLog
from apps.rbac.serializers import DepartmentSerializer
from apps.users.serializers import UserBriefSerializer


class DepartmentSignatureSerializer(serializers.ModelSerializer):
    """部门签章序列化器"""
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = DepartmentSignature
        fields = ['id', 'department', 'department_id', 'name', 'signature_image', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class ElectronicFileListSerializer(serializers.ModelSerializer):
    """电子文件列表序列化器"""
    department = DepartmentSerializer(read_only=True)
    signature = DepartmentSignatureSerializer(read_only=True)
    signer = UserBriefSerializer(read_only=True)
    recipient_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ElectronicFile
        fields = [
            'id', 'title', 'description', 'file_name', 'file_size', 'file_size_display',
            'file_type', 'department', 'signature', 'signer', 'signed_at',
            'status', 'created_at', 'recipient_count', 'unread_count'
        ]
    
    def get_recipient_count(self, obj):
        return obj.recipients.count()
    
    def get_unread_count(self, obj):
        return obj.recipients.filter(is_read=False).count()


class ElectronicFileDetailSerializer(serializers.ModelSerializer):
    """电子文件详情序列化器"""
    department = DepartmentSerializer(read_only=True)
    signature = DepartmentSignatureSerializer(read_only=True)
    signer = UserBriefSerializer(read_only=True)
    recipients = serializers.SerializerMethodField()
    verification_result = serializers.SerializerMethodField()
    
    class Meta:
        model = ElectronicFile
        fields = [
            'id', 'title', 'description', 'file', 'file_name', 'file_size', 'file_size_display',
            'file_type', 'content_type', 'department', 'signature', 'signer', 'signed_at',
            'signature_hash', 'status', 'created_at', 'updated_at', 'recipients',
            'verification_result'
        ]
    
    def get_recipients(self, obj):
        recipients = FileRecipient.objects.filter(file=obj)
        return [{
            'id': r.id,
            'user': UserBriefSerializer(r.recipient).data,
            'is_read': r.is_read,
            'read_at': r.read_at
        } for r in recipients]
    
    def get_verification_result(self, obj):
        if obj.status == 'signed' or obj.status == 'sent':
            is_valid, message = obj.verify_signature()
            return {
                'is_valid': is_valid,
                'message': message
            }
        return None


class ElectronicFileCreateSerializer(serializers.ModelSerializer):
    """电子文件创建序列化器"""
    department_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ElectronicFile
        fields = [
            'id', 'title', 'description', 'file', 'department_id'
        ]
    
    def create(self, validated_data):
        department_id = validated_data.pop('department_id')
        from apps.rbac.models import Department
        department = Department.objects.get(id=department_id)
        validated_data['department'] = department
        return super().create(validated_data)


class FileRecipientSerializer(serializers.ModelSerializer):
    """文件接收人序列化器"""
    recipient = UserBriefSerializer(read_only=True)
    recipient_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FileRecipient
        fields = ['id', 'recipient', 'recipient_id', 'is_read', 'read_at', 'created_at']


class SignatureOperationLogSerializer(serializers.ModelSerializer):
    """签章操作日志序列化器"""
    user = UserBriefSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    file = ElectronicFileListSerializer(read_only=True)
    
    class Meta:
        model = SignatureOperationLog
        fields = [
            'id', 'operation', 'file', 'user', 'department',
            'ip_address', 'user_agent', 'details', 'created_at'
        ]
        read_only_fields = ['created_at']


class SignFileSerializer(serializers.Serializer):
    """文件签章序列化器"""
    signature_id = serializers.IntegerField(required=True)


class SendFileSerializer(serializers.Serializer):
    """文件发送序列化器"""
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    send_all = serializers.BooleanField(default=False)
    departments = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )


class VerifyFileSerializer(serializers.Serializer):
    """文件验签序列化器"""
    file_id = serializers.IntegerField(required=True)
