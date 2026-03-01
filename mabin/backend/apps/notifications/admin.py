from django.contrib import admin
from .models import Notification, NotificationRead, NotificationAttachment, NotificationSetting, NotificationLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'sender', 'business_type', 'notification_type', 'priority', 'status', 'total_recipients', 'read_count', 'created_at']
    list_filter = ['business_type', 'priority', 'status', 'notification_type', 'created_at']
    search_fields = ['title', 'content', 'sender__username', 'sender__real_name']
    raw_id_fields = ['sender', 'recipients']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'sender', 'priority', 'status')
        }),
        ('业务关联', {
            'fields': ('business_type', 'business_id', 'business_model', 'business_action')
        }),
        ('跳转链接', {
            'fields': ('link_url', 'link_params')
        }),
        ('待办设置', {
            'fields': ('need_action', 'action_status')
        }),
        ('接收人设置', {
            'fields': ('notification_type', 'recipients', 'recipient_roles', 'recipient_departments')
        }),
        ('统计信息', {
            'fields': ('total_recipients', 'read_count'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'sent_at', 'recalled_at', 'expire_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'sent_at', 'recalled_at', 'total_recipients', 'read_count']


@admin.register(NotificationRead)
class NotificationReadAdmin(admin.ModelAdmin):
    list_display = ['notification', 'user', 'is_read', 'read_at', 'read_device', 'is_handled', 'handled_at']
    list_filter = ['is_read', 'is_handled', 'read_device', 'created_at']
    search_fields = ['notification__title', 'user__username', 'user__real_name']
    raw_id_fields = ['notification', 'user']
    date_hierarchy = 'created_at'


@admin.register(NotificationAttachment)
class NotificationAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'notification', 'file_size', 'created_at']
    list_filter = ['created_at']
    search_fields = ['filename', 'notification__title']
    raw_id_fields = ['notification']
    date_hierarchy = 'created_at'


@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ['user', 'workflow_enabled', 'file_enabled', 'academic_enabled', 'warning_enabled', 'activity_enabled', 'updated_at']
    list_filter = ['workflow_enabled', 'file_enabled', 'academic_enabled', 'warning_enabled', 'activity_enabled']
    search_fields = ['user__username', 'user__real_name']
    raw_id_fields = ['user']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'notification', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'user__real_name', 'notification__title', 'details']
    raw_id_fields = ['notification', 'user']
    date_hierarchy = 'created_at'
    readonly_fields = ['action', 'notification', 'user', 'ip_address', 'user_agent', 'details', 'created_at']
    
    fieldsets = (
        ('操作信息', {
            'fields': ('action', 'notification', 'user', 'created_at')
        }),
        ('设备信息', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('详细信息', {
            'fields': ('details',)
        }),
    )
