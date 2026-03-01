from rest_framework import serializers
from apps.students.serializers import StudentSerializer
from apps.users.serializers import UserSerializer
from .models import AwardType, AwardApplication, AwardPublicity


class AwardTypeSerializer(serializers.ModelSerializer):
    """奖项类型序列化器"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AwardType
        fields = [
            'id', 'name', 'category', 'category_display', 'level',
            'amount', 'description', 'criteria',
            'is_active', 'application_start', 'application_end',
            'applications_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_applications_count(self, obj):
        return obj.applications.count() if hasattr(obj, 'applications') else 0


class AwardApplicationSerializer(serializers.ModelSerializer):
    """评奖评优申请序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    award_type_name = serializers.CharField(source='award_type.name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.real_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AwardApplication
        fields = [
            'id', 'student', 'student_name', 'student_id',
            'award_type', 'award_type_name', 'status', 'status_display',
            'application_reason', 'achievements', 'attachments',
            'match_score', 'match_details',
            'reviewer', 'reviewer_name', 'review_comment', 'review_time',
            'publicize_start', 'publicize_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'match_score', 'reviewer', 'review_time', 'created_at', 'updated_at']


class AwardPublicitySerializer(serializers.ModelSerializer):
    """公示记录序列化器"""
    application_info = AwardApplicationSerializer(source='application', read_only=True)
    
    class Meta:
        model = AwardPublicity
        fields = [
            'id', 'application', 'application_info',
            'title', 'content', 'start_time', 'end_time',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
