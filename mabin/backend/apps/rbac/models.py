from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Department(models.Model):
    """部门/组织架构"""
    name = models.CharField('部门名称', max_length=100, unique=True)
    code = models.CharField('部门编码', max_length=50, unique=True, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级部门'
    )
    leader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_departments',
        verbose_name='部门负责人'
    )
    description = models.TextField('描述', blank=True)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'departments'
        verbose_name = '部门'
        verbose_name_plural = '部门'
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.name


class Role(models.Model):
    """角色 - 只做登录身份区分，控制能进哪个页面"""
    ROLE_TYPES = [
        ('admin', '管理员'),
        ('student', '学生'),
        ('teacher', '教师'),
        ('staff', '职工'),
    ]
    
    name = models.CharField('角色名称', max_length=50, unique=True)
    code = models.CharField('角色编码', max_length=50, unique=True)
    role_type = models.CharField('角色类型', max_length=20, choices=ROLE_TYPES)
    description = models.TextField('描述', blank=True)
    is_system = models.BooleanField('系统角色', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['id']
    
    def __str__(self):
        return self.name


class Permission(models.Model):
    """权限"""
    PERMISSION_TYPES = [
        ('menu', '菜单权限'),
        ('button', '按钮权限'),
        ('api', 'API权限'),
    ]
    
    name = models.CharField('权限名称', max_length=100)
    code = models.CharField('权限编码', max_length=100, unique=True)
    permission_type = models.CharField('权限类型', max_length=20, choices=PERMISSION_TYPES)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父权限'
    )
    path = models.CharField('路径/路由', max_length=200, blank=True)
    method = models.CharField('HTTP方法', max_length=10, blank=True)  # GET, POST, PUT, DELETE
    description = models.TextField('描述', blank=True)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'permissions'
        verbose_name = '权限'
        verbose_name_plural = '权限'
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """角色权限关联"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'role_permissions'
        verbose_name = '角色权限'
        verbose_name_plural = '角色权限'
        unique_together = ['role', 'permission']
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserRole(models.Model):
    """用户角色关联"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'user_roles'
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.real_name} - {self.role.name}"


POSITION_CHOICES = [
    ('student', '学生'),
    ('teacher', '教师'),
    ('secretary', '教学秘书'),
    ('dean', '院长/系主任'),
    ('secretary_party', '书记'),
    ('clerk', '干事/科员'),
    ('section_chief', '科长'),
    ('deputy_director', '副处长'),
    ('director', '处长'),
    ('deputy_bureau', '副厅长'),
    ('bureau_chief', '厅长'),
]


class UserPosition(models.Model):
    """用户职务表 - 控制能审批什么、管哪个部门"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_positions',
        verbose_name='用户'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='position_holders',
        verbose_name='所属部门'
    )
    position_code = models.CharField('职务编码', max_length=30, choices=POSITION_CHOICES)
    is_main = models.BooleanField('是否主职务', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'user_positions'
        verbose_name = '用户职务'
        verbose_name_plural = '用户职务'
        ordering = ['-is_main', 'id']
    
    def __str__(self):
        return f"{self.user.real_name} - {self.department.name} - {self.get_position_code_display()}"
