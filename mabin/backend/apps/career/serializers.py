from rest_framework import serializers
from apps.students.serializers import StudentSerializer
from .models import (
    Company, JobPosting, Resume, JobApplication,
    JobFair, JobFairRegistration, EmploymentStatistics
)


class CompanySerializer(serializers.ModelSerializer):
    """企业序列化器"""
    scale_display = serializers.CharField(source='get_scale_display', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'industry', 'scale', 'scale_display', 'address',
            'website', 'description', 'logo', 'contact_person', 'contact_phone',
            'contact_email', 'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class JobPostingSerializer(serializers.ModelSerializer):
    """招聘信息序列化器"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.CharField(source='company.logo.url', read_only=True)
    job_type_display = serializers.CharField(source='get_job_type_display', read_only=True)
    salary_range = serializers.SerializerMethodField()
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'company', 'company_name', 'company_logo', 'title', 'department',
            'job_type', 'job_type_display', 'salary_min', 'salary_max', 'salary_range',
            'location', 'description', 'requirements', 'benefits', 'deadline',
            'is_active', 'views_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'views_count', 'created_at', 'updated_at']
    
    def get_salary_range(self, obj):
        if obj.salary_min and obj.salary_max:
            return f"{obj.salary_min}-{obj.salary_max}K"
        elif obj.salary_min:
            return f"{obj.salary_min}K以上"
        return "面议"


class ResumeSerializer(serializers.ModelSerializer):
    """简历序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    
    class Meta:
        model = Resume
        fields = [
            'id', 'student', 'student_name', 'name', 'personal_info',
            'education', 'experience', 'skills', 'projects', 'awards',
            'self_introduction', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JobApplicationSerializer(serializers.ModelSerializer):
    """职位申请序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_title', 'company_name', 'student', 'student_name',
            'resume', 'status', 'status_display', 'cover_letter',
            'applied_at', 'viewed_at'
        ]
        read_only_fields = ['id', 'applied_at', 'viewed_at']


class JobFairSerializer(serializers.ModelSerializer):
    """招聘会序列化器"""
    companies_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    
    class Meta:
        model = JobFair
        fields = [
            'id', 'name', 'description', 'location', 'start_time', 'end_time',
            'max_participants', 'current_participants', 'companies_count',
            'is_registered', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'current_participants', 'created_at']
    
    def get_companies_count(self, obj):
        return obj.companies.count()
    
    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student_profile'):
            return JobFairRegistration.objects.filter(
                job_fair=obj,
                student=request.user.student_profile
            ).exists()
        return False


class EmploymentStatisticsSerializer(serializers.ModelSerializer):
    """就业统计序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    employment_status_display = serializers.CharField(source='get_employment_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    
    class Meta:
        model = EmploymentStatistics
        fields = [
            'id', 'student', 'student_name', 'employment_status', 'employment_status_display',
            'company', 'company_name', 'position', 'salary', 'location',
            'employment_date', 'source', 'source_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
