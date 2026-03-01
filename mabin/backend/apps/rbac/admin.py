from django.contrib import admin
from .models import Department, Role, Permission, RolePermission, UserRole


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'leader', 'is_active', 'order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'code']
    raw_id_fields = ['parent', 'leader']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'role_type', 'is_system', 'is_active', 'created_at']
    list_filter = ['role_type', 'is_system', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'permission_type', 'path', 'method', 'parent', 'order', 'is_active']
    list_filter = ['permission_type', 'is_active', 'parent']
    search_fields = ['name', 'code', 'path']
    raw_id_fields = ['parent']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'created_at']
    list_filter = ['role', 'permission']
    raw_id_fields = ['role', 'permission']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']
    list_filter = ['role']
    raw_id_fields = ['user', 'role']
