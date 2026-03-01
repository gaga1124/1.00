"""
权限检查工具
"""
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()


class IsSuperAdmin(BasePermission):
    """超级管理员权限"""
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class HasRolePermission(BasePermission):
    """角色权限检查"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 获取需要的角色代码
        required_roles = getattr(view, 'required_roles', [])
        if not required_roles:
            return True
        
        # 检查用户是否拥有所需角色
        from apps.rbac.models import UserRole
        user_roles = UserRole.objects.filter(user=request.user).values_list('role__code', flat=True)
        
        return any(role in user_roles for role in required_roles)


class HasPermission(BasePermission):
    """权限代码检查"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 获取需要的权限代码
        required_permissions = getattr(view, 'required_permissions', [])
        if not required_permissions:
            return True
        
        # 检查用户是否拥有所需权限
        from apps.rbac.models import UserRole, RolePermission
        user_roles = UserRole.objects.filter(user=request.user).values_list('role', flat=True)
        user_permissions = RolePermission.objects.filter(
            role__in=user_roles
        ).values_list('permission__code', flat=True)
        
        return any(perm in user_permissions for perm in required_permissions)
