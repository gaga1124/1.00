from rest_framework import serializers
from apps.students.serializers import StudentSerializer
from .models import Company, JobPosting, JobApplication, JobFair, JobFairRegistration, EmploymentStatistics


class CompanySerializer(serializers.ModelSerializer):
    """企业序列化器"""
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'industry', 'scale', 'address', 'website',
            'description', 'logo', 'contact_name', 'contact_phone',
            'contact_email', 'is_verified', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class JobPostingSerializer(serializers.ModelSerializer):
    """招聘信息序列化器"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.ImageField(source='company.logo', read_only=True)
    is_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'company', 'company_name', 'company_logo',
            'title', 'department', 'job_description', 'requirements',
            'salary_range', 'location', 'recruitment_number', 'applied_count',
            'is_applied', 'publish_time', 'deadline', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'applied_count', 'publish_time', 'created_at']
    
    def get_is_applied(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student_profile'):
            return JobApplication.objects.filter(
                student=request.user.student_profile,
                job_posting=obj
            ).exists()
        return False


class JobApplicationSerializer(serializers.ModelSerializer):
    """简历投递序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    job_title = serializers.CharField(source='job_posting.title', read_only=True)
    company_name = serializers.CharField(source='job_posting.company.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'student', 'student_name', 'job_posting', 'job_title',
            'company_name', 'status', 'status_display',
            'resume', 'cover_letter', 'applied_at', 'viewed_at'
        ]
        read_only_fields = ['id', 'applied_at', 'viewed_at']


class JobFairSerializer(serializers.ModelSerializer):
    """招聘会序列化器"""
    companies_info = CompanySerializer(source='companies', many=True, read_only=True)
    is_registered = serializers.SerializerMethodField()
    can_register = serializers.SerializerMethodField()
    
    class Meta:
        model = JobFair
        fields = [
            'id', 'title', 'description', 'location',
            'start_time', 'end_time',
            'registration_start', 'registration_end',
            'capacity', 'registered_count', 'is_registered', 'can_register',
            'companies', 'companies_info', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'registered_count', 'created_at']
    
    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student_profile'):
            return JobFairRegistration.objects.filter(
                student=request.user.student_profile,
                job_fair=obj
            ).exists()
        return False
    
    def get_can_register(self, obj):
        from django.utils import timezone
        now = timezone.now()
        if obj.registration_start > now or obj.registration_end < now:
            return False
        if obj.capacity > 0 and obj.registered_count >= obj.capacity:
            return False
        return True


class JobFairRegistrationSerializer(serializers.ModelSerializer):
    """招聘会报名序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    job_fair_title = serializers.CharField(source='job_fair.title', read_only=True)
    
    class Meta:
        model = JobFairRegistration
        fields = ['id', 'student', 'student_name', 'job_fair', 'job_fair_title', 'registered_at']
        read_only_fields = ['id', 'registered_at']


class EmploymentStatisticsSerializer(serializers.ModelSerializer):
    """就业数据序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = EmploymentStatistics
        fields = [
            'id', 'student', 'student_name', 'is_employed', 'employment_type',
            'company', 'company_name', 'position', 'salary', 'location',
            'employment_date', 'graduation_year', 'major_match', 'satisfaction',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
