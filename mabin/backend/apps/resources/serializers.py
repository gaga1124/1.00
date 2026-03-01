from rest_framework import serializers
from apps.users.serializers import UserSerializer
from .models import ResourceCategory, Resource, ResourceBooking


class ResourceCategorySerializer(serializers.ModelSerializer):
    """资源分类序列化器"""
    class Meta:
        model = ResourceCategory
        fields = ['id', 'name', 'description', 'order', 'is_active', 'created_at']


class ResourceSerializer(serializers.ModelSerializer):
    """资源序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    approver_name = serializers.CharField(source='approver.real_name', read_only=True)
    
    class Meta:
        model = Resource
        fields = [
            'id', 'name', 'resource_type', 'resource_type_display', 'category', 'category_name',
            'department', 'department_name', 'location', 'capacity', 'equipment', 'description', 'images',
            'advance_booking_days', 'min_booking_hours', 'max_booking_hours',
            'require_approval', 'approver', 'approver_name', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResourceBookingSerializer(serializers.ModelSerializer):
    """资源预约序列化器"""
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    resource_type = serializers.CharField(source='resource.resource_type', read_only=True)
    applicant_name = serializers.CharField(source='applicant.real_name', read_only=True)
    approver_name = serializers.CharField(source='approver.real_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ResourceBooking
        fields = [
            'id', 'resource', 'resource_name', 'resource_type', 'applicant', 'applicant_name',
            'title', 'description', 'start_time', 'end_time', 'status', 'status_display',
            'approver', 'approver_name', 'approval_comment', 'approval_time',
            'contact_name', 'contact_phone', 'attachments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'approver', 'approval_time', 'created_at', 'updated_at']
