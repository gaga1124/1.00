from rest_framework import serializers
from apps.users.serializers import UserSerializer
from .models import RepairCategory, RepairApplication, RepairRecord


class RepairCategorySerializer(serializers.ModelSerializer):
    """报修分类序列化器"""
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RepairCategory
        fields = [
            'id', 'name', 'icon', 'description', 'order',
            'is_active', 'applications_count', 'created_at'
        ]
    
    def get_applications_count(self, obj):
        return obj.applications.count() if hasattr(obj, 'applications') else 0


class RepairRecordSerializer(serializers.ModelSerializer):
    """报修处理记录序列化器"""
    operator_name = serializers.CharField(source='operator.real_name', read_only=True)
    
    class Meta:
        model = RepairRecord
        fields = [
            'id', 'application', 'operator', 'operator_name',
            'action', 'comment', 'images', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RepairApplicationSerializer(serializers.ModelSerializer):
    """报修申请序列化器"""
    applicant = serializers.HiddenField(default=serializers.CurrentUserDefault())
    applicant_name = serializers.CharField(source='applicant.real_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    handler_name = serializers.CharField(source='handler.real_name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    records = RepairRecordSerializer(many=True, read_only=True)
    can_handle = serializers.SerializerMethodField()
    
    class Meta:
        model = RepairApplication
        fields = [
            'id', 'applicant', 'applicant_name', 'category', 'category_name',
            'title', 'description', 'location', 'priority', 'priority_display',
            'status', 'status_display', 'contact_name', 'contact_phone',
            'images', 'handler', 'handler_name', 'accepted_at', 'completed_at',
            'handler_comment', 'applicant_comment', 'rating', 'extra_data',
            'records', 'can_handle', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'handler', 'accepted_at', 'completed_at',
            'created_at', 'updated_at'
        ]

    def get_can_handle(self, obj):
        """当前用户是否有权限处理该报修"""
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        # 后勤处判断（基于角色）
        is_logistics = False
        try:
            is_logistics = bool(getattr(user, 'has_role', None) and user.has_role('logistics'))
        except Exception:
            is_logistics = False
        # 管理员/超级管理员/后勤处 或 指定处理人
        return bool(user.is_superuser or user.is_staff or is_logistics or (obj.handler_id == user.id))
