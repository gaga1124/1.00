from django.contrib import admin
from .models import RepairCategory, RepairApplication, RepairRecord


@admin.register(RepairCategory)
class RepairCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['order']


@admin.register(RepairApplication)
class RepairApplicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'applicant', 'priority', 'status', 'handler', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['title', 'description', 'location', 'applicant__real_name']
    raw_id_fields = ['applicant', 'category', 'handler']
    readonly_fields = ['created_at', 'updated_at', 'accepted_at', 'completed_at']


@admin.register(RepairRecord)
class RepairRecordAdmin(admin.ModelAdmin):
    list_display = ['application', 'operator', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['application__title', 'operator__real_name']
    raw_id_fields = ['application', 'operator']
