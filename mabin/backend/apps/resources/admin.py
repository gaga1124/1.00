from django.contrib import admin
from .models import ResourceCategory, Resource, ResourceBooking


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'resource_type', 'location', 'capacity', 'require_approval', 'is_active']
    list_filter = ['resource_type', 'require_approval', 'is_active', 'category']
    search_fields = ['name', 'location']
    raw_id_fields = ['category', 'approver']


@admin.register(ResourceBooking)
class ResourceBookingAdmin(admin.ModelAdmin):
    list_display = ['resource', 'applicant', 'title', 'start_time', 'end_time', 'status', 'created_at']
    list_filter = ['status', 'resource', 'created_at']
    search_fields = ['title', 'applicant__real_name', 'resource__name']
    raw_id_fields = ['resource', 'applicant', 'approver']
