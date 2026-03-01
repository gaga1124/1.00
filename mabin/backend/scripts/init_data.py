"""
初始化数据脚本
用于创建系统预设角色、权限等基础数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_oa.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.rbac.models import Role, Permission, Department

User = get_user_model()


def create_roles():
    """创建系统预设角色"""
    roles = [
        {'name': '超级管理员', 'code': 'super_admin', 'role_type': 'super_admin', 'is_system': True},
        {'name': '院领导', 'code': 'leader', 'role_type': 'leader', 'is_system': True},
        {'name': '行政秘书', 'code': 'secretary', 'role_type': 'secretary', 'is_system': True},
        {'name': '后勤处', 'code': 'logistics', 'role_type': 'logistics', 'is_system': True},
        {'name': '财务处', 'code': 'finance', 'role_type': 'leader', 'is_system': True},
        {'name': '财务处负责人', 'code': 'finance_director', 'role_type': 'leader', 'is_system': True},
        {'name': '科研管理员', 'code': 'research_admin', 'role_type': 'leader', 'is_system': True},
        {'name': '资源管理员', 'code': 'resource_admin', 'role_type': 'leader', 'is_system': True},
        {'name': '辅导员', 'code': 'counselor', 'role_type': 'counselor', 'is_system': True},
        {'name': '任课教师', 'code': 'teacher', 'role_type': 'teacher', 'is_system': True},
        {'name': '学生', 'code': 'student', 'role_type': 'student', 'is_system': True},
    ]
    
    for role_data in roles:
        role, created = Role.objects.get_or_create(
            code=role_data['code'],
            defaults=role_data
        )
        if created:
            print(f"创建角色: {role.name}")
        else:
            print(f"角色已存在: {role.name}")


def create_departments():
    """创建示例部门"""
    departments = [
        {'name': '学院办公室', 'code': 'office'},
        {'name': '教学管理部', 'code': 'teaching'},
        {'name': '学生工作部', 'code': 'student_affairs'},
        {'name': '科研管理部', 'code': 'research'},
    ]
    
    for dept_data in departments:
        dept, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults=dept_data
        )
        if created:
            print(f"创建部门: {dept.name}")
        else:
            print(f"部门已存在: {dept.name}")


def create_permissions():
    """创建基础权限"""
    permissions = [
        # 学生管理权限
        {'name': '查看学生', 'code': 'student:view', 'permission_type': 'menu'},
        {'name': '编辑学生', 'code': 'student:edit', 'permission_type': 'button'},
        {'name': '删除学生', 'code': 'student:delete', 'permission_type': 'button'},
        
        # 流程管理权限
        {'name': '查看流程', 'code': 'workflow:view', 'permission_type': 'menu'},
        {'name': '创建流程', 'code': 'workflow:create', 'permission_type': 'button'},
        {'name': '审批流程', 'code': 'workflow:approve', 'permission_type': 'button'},
        
        # 资源管理权限
        {'name': '查看资源', 'code': 'resource:view', 'permission_type': 'menu'},
        {'name': '预约资源', 'code': 'resource:book', 'permission_type': 'button'},
        {'name': '审批预约', 'code': 'resource:approve', 'permission_type': 'button'},
        
        # 审批管理权限
        {'name': '查看审批', 'code': 'approval:view', 'permission_type': 'menu'},
        {'name': '创建审批', 'code': 'approval:create', 'permission_type': 'button'},
        {'name': '审批申请', 'code': 'approval:approve', 'permission_type': 'button'},
    ]
    
    for perm_data in permissions:
        perm, created = Permission.objects.get_or_create(
            code=perm_data['code'],
            defaults=perm_data
        )
        if created:
            print(f"创建权限: {perm.name}")
        else:
            print(f"权限已存在: {perm.name}")


if __name__ == '__main__':
    print("开始初始化数据...")
    create_roles()
    create_departments()
    create_permissions()
    print("数据初始化完成！")
