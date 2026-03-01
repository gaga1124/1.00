from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import Department, Role, Permission, RolePermission, UserRole, UserPosition
from .serializers import (
    DepartmentSerializer, RoleSerializer, PermissionSerializer,
    RolePermissionSerializer, UserRoleSerializer, UserPositionSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """部门视图集"""
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """获取子部门"""
        department = self.get_object()
        children = department.children.filter(is_active=True)
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取部门树"""
        roots = Department.objects.filter(parent=None, is_active=True)
        serializer = self.get_serializer(roots, many=True)
        return Response(serializer.data)


class RoleViewSet(viewsets.ModelViewSet):
    """角色视图集"""
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get', 'post', 'delete'])
    def permissions(self, request, pk=None):
        """角色权限管理"""
        role = self.get_object()
        
        if request.method == 'GET':
            # 获取角色权限列表
            permissions = Permission.objects.filter(
                role_permissions__role=role
            )
            serializer = PermissionSerializer(permissions, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # 添加权限
            permission_ids = request.data.get('permission_ids', [])
            for perm_id in permission_ids:
                RolePermission.objects.get_or_create(
                    role=role,
                    permission_id=perm_id
                )
            return Response({'message': '权限添加成功'})
        
        elif request.method == 'DELETE':
            # 删除权限
            permission_id = request.data.get('permission_id')
            if permission_id:
                RolePermission.objects.filter(
                    role=role,
                    permission_id=permission_id
                ).delete()
            return Response({'message': '权限删除成功'})


class PermissionViewSet(viewsets.ModelViewSet):
    """权限视图集"""
    queryset = Permission.objects.filter(is_active=True)
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取权限树"""
        roots = Permission.objects.filter(parent=None, is_active=True)
        serializer = self.get_serializer(roots, many=True)
        return Response(serializer.data)


class RolePermissionViewSet(viewsets.ModelViewSet):
    """角色权限关联视图集"""
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]


class UserRoleViewSet(viewsets.ModelViewSet):
    """用户角色关联视图集"""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_roles(self, request):
        """获取当前用户角色"""
        user_roles = UserRole.objects.filter(user=request.user)
        serializer = self.get_serializer(user_roles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_modify(self, request):
        """批量修改用户角色
        
        请求体：
        {
          "user_ids": [1,2,3],
          "role_code": "teacher",   // 或传 role_id
          "role_id": 5,
          "mode": "add" | "remove" | "set"
        }
        """
        user = request.user
        # 权限：仅超级管理员或后台职员
        has_super_role = False
        try:
            # 避免循环导入，延迟判断
            has_super_role = hasattr(user, 'has_role') and user.has_role('super_admin')
        except Exception:
            has_super_role = False
        if not (user.is_superuser or user.is_staff or has_super_role):
            return Response({'error': '没有权限执行批量角色变更'}, status=403)
        
        user_ids = request.data.get('user_ids') or []
        role_code = request.data.get('role_code')
        role_id = request.data.get('role_id')
        mode = (request.data.get('mode') or 'add').lower()
        
        if not isinstance(user_ids, list) or not user_ids:
            return Response({'error': 'user_ids 必须为非空数组'}, status=400)
        
        role = None
        if role_id:
            role = Role.objects.filter(id=role_id, is_active=True).first()
        elif role_code:
            role = Role.objects.filter(code=role_code, is_active=True).first()
        
        if not role:
            return Response({'error': '指定的角色不存在或未启用'}, status=400)
        
        qs = self.queryset.model._meta.apps.get_model('users', 'User').objects.filter(id__in=user_ids)
        added = removed = set_count = 0
        
        with transaction.atomic():
            if mode == 'set':
                for u in qs:
                    UserRole.objects.filter(user=u).delete()
                set_count = qs.count()
                bulk = [UserRole(user=u, role=role) for u in qs]
                UserRole.objects.bulk_create(bulk, ignore_conflicts=True)
            elif mode == 'add':
                for u in qs:
                    _, created = UserRole.objects.get_or_create(user=u, role=role)
                    if created:
                        added += 1
            elif mode == 'remove':
                for u in qs:
                    removed += UserRole.objects.filter(user=u, role=role).delete()[0]
            else:
                return Response({'error': 'mode 只能是 add/remove/set'}, status=400)
        
        return Response({
            'role': {'id': role.id, 'code': role.code, 'name': role.name},
            'mode': mode,
            'affected_users': len(user_ids),
            'added': added,
            'removed': removed,
            'set': set_count
        })


class UserPositionViewSet(viewsets.ModelViewSet):
    """用户职务视图集"""
    queryset = UserPosition.objects.all()
    serializer_class = UserPositionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'department', 'position_code', 'is_main']
    search_fields = ['user__real_name', 'department__name']
    ordering_fields = ['id', 'is_main', 'created_at']
    
    @action(detail=False, methods=['delete'])
    def clear_by_user(self, request):
        """清除用户所有职务"""
        user_id = request.data.get('user')
        if not user_id:
            return Response({'error': '请提供用户ID'}, status=400)
        deleted, _ = UserPosition.objects.filter(user_id=user_id).delete()
        return Response({'deleted': deleted})
    
    @action(detail=False, methods=['get'])
    def my_positions(self, request):
        """获取当前用户职务"""
        user_positions = UserPosition.objects.filter(user=request.user)
        serializer = self.get_serializer(user_positions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_info(self, request):
        """获取当前用户完整信息（角色+职务+部门）"""
        user = request.user
        
        # 获取角色
        roles = UserRole.objects.filter(user=user).select_related('role')
        role_data = []
        role_type = None
        for ur in roles:
            role_data.append({
                'role_id': ur.role.id,
                'role_name': ur.role.name,
                'role_type': ur.role.role_type
            })
            if ur.role.role_type:
                role_type = ur.role.role_type
        
        # 获取职务
        positions = UserPosition.objects.filter(user=user).select_related('department')
        position_data = []
        main_dept_id = None
        for pos in positions:
            position_data.append({
                'position_id': pos.id,
                'department_id': pos.department.id,
                'department_name': pos.department.name,
                'position_code': pos.position_code,
                'position_name': pos.get_position_code_display(),
                'is_main': pos.is_main
            })
            if pos.is_main:
                main_dept_id = pos.department.id
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'role_type': role_type,
            'roles': role_data,
            'positions': position_data,
            'main_department_id': main_dept_id
        })
