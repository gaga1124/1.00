from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """用户档案序列化器"""
    class Meta:
        model = UserProfile
        fields = ['job_title', 'employee_id', 'bio', 'extra_data']


class UserBriefSerializer(serializers.ModelSerializer):
    """用户简要信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'avatar']


class TeacherSerializer(serializers.ModelSerializer):
    """教师序列化器"""
    profile = UserProfileSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'real_name', 'gender', 'phone', 'email',
            'avatar', 'department', 'department_name', 'is_active',
            'created_at', 'profile'
        ]
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    profile = UserProfileSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    role = serializers.SerializerMethodField()
    role_type = serializers.SerializerMethodField()
    role_list = serializers.SerializerMethodField()
    positions = serializers.SerializerMethodField()
    main_department = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'real_name', 'gender', 'phone', 'id_card', 'email',
            'avatar', 'department', 'department_name', 'is_active',
            'is_staff', 'is_superuser', 'created_at', 'profile', 'role', 'role_type', 'role_list', 'positions', 'main_department'
        ]
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'created_at']

    def get_role(self, obj):
        if getattr(obj, 'is_superuser', False):
            return 'admin'
        try:
            from apps.rbac.models import UserRole
            role_codes = set(UserRole.objects.filter(user=obj).values_list('role__code', flat=True))
            if 'admin' in role_codes:
                return 'admin'
            if 'teacher' in role_codes:
                return 'teacher'
            if 'staff' in role_codes:
                return 'staff'
            if 'student' in role_codes:
                return 'student'
        except Exception:
            pass
        return 'student'
    
    def get_role_list(self, obj):
        try:
            from apps.rbac.models import UserRole
            roles = UserRole.objects.filter(user=obj).select_related('role')
            return [{'id': ur.role.id, 'name': ur.role.name, 'code': ur.role.code, 'role_type': ur.role.role_type} for ur in roles]
        except Exception:
            return []

    def get_role_type(self, obj):
        try:
            from apps.rbac.models import UserRole
            ur = UserRole.objects.filter(user=obj).select_related('role').first()
            if ur:
                return ur.role.role_type
        except Exception:
            pass
        return 'student'

    def get_positions(self, obj):
        try:
            from apps.rbac.models import UserPosition
            positions = UserPosition.objects.filter(user=obj).select_related('department')
            return [{
                'id': p.id,
                'department_id': p.department.id,
                'department_name': p.department.name,
                'position_code': p.position_code,
                'position_name': p.get_position_code_display(),
                'is_main': p.is_main
            } for p in positions]
        except Exception:
            return []
    
    def get_main_department(self, obj):
        try:
            from apps.rbac.models import UserPosition
            main_pos = UserPosition.objects.filter(user=obj, is_main=True).select_related('department').first()
            if main_pos:
                return {'id': main_pos.department.id, 'name': main_pos.department.name}
        except Exception:
            pass
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    employee_id = serializers.CharField(write_only=True, label='工号')
    role_code = serializers.ChoiceField(
        choices=[('teacher', '教师'), ('student', '学生'), ('staff', '职工')],
        write_only=True,
        required=True
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'password', 'real_name', 'gender', 'phone', 'id_card', 'email',
            'department', 'employee_id', 'role_code'
        ]
        extra_kwargs = {
            'username': {'required': True},
            'real_name': {'required': True},
            'department': {'required': True}
        }

    def create(self, validated_data):
        employee_id = validated_data.pop('employee_id')
        role_code = validated_data.pop('role_code')
        
        if not validated_data.get('password'):
            validated_data['password'] = '123456'  # 默认密码
        
        user = User.objects.create_user(**validated_data)
        
        # 创建用户档案
        UserProfile.objects.create(user=user, employee_id=employee_id)
        
        # 分配角色
        try:
            from apps.rbac.models import Role, UserRole
            role = Role.objects.filter(code=role_code).first()
            if role:
                UserRole.objects.create(user=user, role=role)
        except Exception:
            pass
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""
    class Meta:
        model = User
        fields = ['real_name', 'gender', 'phone', 'email', 'avatar', 'department']


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')
        return {'user': user}
