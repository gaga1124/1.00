from django.contrib import admin
from .models import DepartmentSignature, ElectronicFile, FileRecipient, SignatureOperationLog


@admin.register(DepartmentSignature)
class DepartmentSignatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department']
    search_fields = ['name', 'department__name']


@admin.register(ElectronicFile)
class ElectronicFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'status', 'signer', 'created_at']
    list_filter = ['status', 'department', 'file_type']
    search_fields = ['title', 'file_name']
    readonly_fields = ['file_size', 'signature_hash', 'signed_at']


@admin.register(FileRecipient)
class FileRecipientAdmin(admin.ModelAdmin):
    list_display = ['file', 'recipient', 'is_read', 'read_at', 'created_at']
    list_filter = ['is_read']
    search_fields = ['file__title', 'recipient__username']


@admin.register(SignatureOperationLog)
class SignatureOperationLogAdmin(admin.ModelAdmin):
    list_display = ['operation', 'user', 'department', 'ip_address', 'created_at']
    list_filter = ['operation', 'department']
    search_fields = ['user__username', 'file__title']
    readonly_fields = ['created_at']
