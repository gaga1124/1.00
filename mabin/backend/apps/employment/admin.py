from django.contrib import admin
from .models import Company, JobPosting, JobApplication, JobFair, JobFairRegistration, EmploymentStatistics


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'scale', 'is_verified', 'is_active', 'created_at']
    list_filter = ['industry', 'is_verified', 'is_active']
    search_fields = ['name', 'contact_name', 'contact_phone']


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'recruitment_number', 'applied_count', 'is_active', 'publish_time']
    list_filter = ['is_active', 'publish_time']
    search_fields = ['title', 'company__name']
    raw_id_fields = ['company']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'job_posting', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['student__student_id', 'student__user__real_name', 'job_posting__title']
    raw_id_fields = ['student', 'job_posting']


@admin.register(JobFair)
class JobFairAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'start_time', 'capacity', 'registered_count', 'is_active']
    list_filter = ['is_active', 'start_time']
    search_fields = ['title']
    filter_horizontal = ['companies']


@admin.register(JobFairRegistration)
class JobFairRegistrationAdmin(admin.ModelAdmin):
    list_display = ['student', 'job_fair', 'registered_at']
    list_filter = ['registered_at']
    search_fields = ['student__student_id', 'student__user__real_name', 'job_fair__title']
    raw_id_fields = ['student', 'job_fair']


@admin.register(EmploymentStatistics)
class EmploymentStatisticsAdmin(admin.ModelAdmin):
    list_display = ['student', 'is_employed', 'employment_type', 'company', 'graduation_year', 'employment_date']
    list_filter = ['is_employed', 'employment_type', 'graduation_year', 'major_match']
    search_fields = ['student__student_id', 'student__user__real_name', 'company__name']
    raw_id_fields = ['student', 'company']
