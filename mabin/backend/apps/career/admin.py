from django.contrib import admin
from .models import (
    Company, JobPosting, Resume, JobApplication,
    JobFair, JobFairRegistration, EmploymentStatistics
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'scale', 'is_verified', 'created_at']
    list_filter = ['industry', 'scale', 'is_verified']
    search_fields = ['name', 'contact_person']


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'job_type', 'location', 'is_active', 'created_at']
    list_filter = ['job_type', 'is_active', 'created_at']
    search_fields = ['title', 'company__name']
    raw_id_fields = ['company']


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['name', 'student', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'student__student_id', 'student__user__real_name']
    raw_id_fields = ['student']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'job', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['student__student_id', 'job__title']
    raw_id_fields = ['job', 'student', 'resume']


@admin.register(JobFair)
class JobFairAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'start_time', 'end_time', 'current_participants', 'is_active']
    list_filter = ['is_active', 'start_time']
    search_fields = ['name', 'location']
    filter_horizontal = ['companies']


@admin.register(JobFairRegistration)
class JobFairRegistrationAdmin(admin.ModelAdmin):
    list_display = ['student', 'job_fair', 'registered_at']
    list_filter = ['registered_at']
    search_fields = ['student__student_id', 'job_fair__name']
    raw_id_fields = ['student', 'job_fair']


@admin.register(EmploymentStatistics)
class EmploymentStatisticsAdmin(admin.ModelAdmin):
    list_display = ['student', 'employment_status', 'company', 'position', 'employment_date']
    list_filter = ['employment_status', 'source', 'employment_date']
    search_fields = ['student__student_id', 'student__user__real_name', 'company__name']
    raw_id_fields = ['student', 'company']
