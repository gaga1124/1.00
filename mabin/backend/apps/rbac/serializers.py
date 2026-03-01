from rest_framework import serializers
from .models import Department, Role, Permission, RolePermission, UserRole, UserPosition
from apps.users.serializers import UserSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    leader_name = serializers.CharField(source='leader.real_name', read_only=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'parent', 'parent_name', 'leader', 'leader_name',
            'description', 'order', 'is_active', 'children_count', 'created_at'
        ]
    
    def get_children_count(self, obj):
        return obj.children.count() if hasattr(obj, 'children') else 0


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'role_type', 'description',
            'is_system', 'is_active', 'permissions_count', 'created_at'
        ]
    
    def get_permissions_count(self, obj):
        return obj.role_permissions.count() if hasattr(obj, 'role_permissions') else 0


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Permission
        fields = [
            'id', 'name', 'code', 'permission_type', 'parent', 'parent_name',
            'path', 'method', 'description', 'order', 'is_active', 'created_at'
        ]


class RolePermissionSerializer(serializers.ModelSerializer):
    """角色权限关联序列化器"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = ['id', 'role', 'role_name', 'permission', 'permission_name', 'created_at']


class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色关联序列化器"""
    user_info = UserSerializer(source='user', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_type = serializers.CharField(source='role.role_type', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'user_info', 'role', 'role_name', 'role_type', 'created_at']


class UserPositionSerializer(serializers.ModelSerializer):
    """用户职务序列化器"""
    user_info = UserSerializer(source='user', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='get_position_code_display', read_only=True)
    
    class Meta:
        model = UserPosition
        fields = [
            'id', 'user', 'user_info', 'department', 'department_name',
            'position_code', 'position_name', 'is_main', 'created_at', 'updated_at'
        ]
