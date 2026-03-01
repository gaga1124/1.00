from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """扩展用户模型"""
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
    ]
    
    # 基础信息
    real_name = models.CharField('真实姓名', max_length=50, blank=True)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField('手机号', max_length=11, blank=True)
    id_card = models.CharField('身份证号', max_length=20, blank=True)
    email = models.EmailField('邮箱', blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    
    # 组织信息
    department = models.ForeignKey(
        'rbac.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name='所属部门'
    )
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    last_login = models.DateTimeField('最后登录', null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.real_name or self.username

    @property
    def roles(self):
        """获取用户所有角色代码"""
        if not hasattr(self, '_roles'):
            from apps.rbac.models import UserRole
            self._roles = list(UserRole.objects.filter(user=self).values_list('role__code', flat=True))
        return self._roles

    def has_role(self, role_code):
        """检查用户是否具有某个角色"""
        return role_code in self.roles

    @property
    def is_secretary(self):
        return self.has_role('secretary')

    @property
    def is_teacher(self):
        return self.has_role('teacher')

    @property
    def is_student_user(self):
        return self.has_role('student')


class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户'
    )
    
    # 工作信息
    job_title = models.CharField('职务', max_length=100, blank=True)
    employee_id = models.CharField('工号', max_length=50, unique=True, null=True, blank=True)
    
    # 个人简介
    bio = models.TextField('个人简介', blank=True)
    
    # 扩展字段（JSON）
    extra_data = models.JSONField('扩展数据', default=dict, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户档案'
        verbose_name_plural = '用户档案'
    
    def __str__(self):
        return f"{self.user.real_name}的档案"
