from django.contrib import admin
from .models import AwardType, AwardApplication, AwardPublicity


@admin.register(AwardType)
class AwardTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'level', 'amount', 'is_active', 'application_start', 'application_end']
    list_filter = ['category', 'level', 'is_active']
    search_fields = ['name']


@admin.register(AwardApplication)
class AwardApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'award_type', 'status', 'match_score', 'reviewer', 'created_at']
    list_filter = ['status', 'award_type', 'created_at']
    search_fields = ['student__student_id', 'student__user__real_name', 'award_type__name']
    raw_id_fields = ['student', 'award_type', 'reviewer']


@admin.register(AwardPublicity)
class AwardPublicityAdmin(admin.ModelAdmin):
    list_display = ['title', 'application', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active', 'created_at']
    raw_id_fields = ['application']
