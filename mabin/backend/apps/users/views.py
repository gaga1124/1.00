from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.hashers import check_password, make_password
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserProfile
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer, UserProfileSerializer,
    TeacherSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'is_active']
    search_fields = ['username', 'real_name', 'phone', 'email']
    ordering_fields = ['created_at', 'username']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_me(self, request):
        """更新当前用户信息"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """用户登录"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # 更新最后登录时间
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """用户登出"""
        # 可以在这里实现token黑名单逻辑
        return Response({'message': '登出成功'})
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """修改密码"""
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({'error': '请提供原密码和新密码'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not check_password(old_password, request.user.password):
            return Response({'error': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6:
            return Response({'error': '新密码长度不能少于6位'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.password = make_password(new_password)
        request.user.save()
        
        return Response({'message': '密码修改成功'})


class UserProfileViewSet(viewsets.ModelViewSet):
    """用户档案视图集"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def my_profile(self, request):
        """获取或更新当前用户档案"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class TeacherViewSet(viewsets.ModelViewSet):
    """教师管理视图集"""
    queryset = User.objects.filter(user_roles__role__code='teacher')
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'is_active', 'profile__job_title']
    search_fields = ['real_name', 'username', 'phone', 'profile__employee_id']
    ordering_fields = ['created_at', 'username', 'profile__employee_id']
    
    def get_queryset(self):
        # Ensure we only get teachers
        return User.objects.filter(user_roles__role__code='teacher')
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """批量创建教师"""
        teachers_data = request.data.get('teachers', [])
        if not teachers_data or not isinstance(teachers_data, list):
            return Response({'error': '请提供教师列表数据'}, status=status.HTTP_400_BAD_REQUEST)
        
        created = []
        errors = []
        
        for idx, data in enumerate(teachers_data):
            try:
                employee_id = data.get('employee_id')
                if not employee_id:
                    errors.append({'index': idx, 'error': '工号不能为空'})
                    continue
                
                real_name = data.get('real_name')
                if not real_name:
                    errors.append({'index': idx, 'error': '姓名不能为空'})
                    continue
                
                department = data.get('department')
                department_name = data.get('department_name', '')
                
                if not department and department_name:
                    from apps.rbac.models import Department
                    dept = Department.objects.filter(name=department_name).first()
                    if dept:
                        department = dept.id
                
                job_title = data.get('job_title', '')
                phone = data.get('phone', '')
                email = data.get('email', '')
                id_card = data.get('id_card', '')
                
                username = employee_id
                password = employee_id
                
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    real_name=real_name,
                    phone=phone,
                    email=email,
                    id_card=id_card,
                    department_id=department
                )
                
                UserProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'job_title': job_title,
                        'employee_id': employee_id
                    }
                )
                
                from apps.rbac.models import Role, UserRole
                role = Role.objects.get(code='teacher')
                UserRole.objects.get_or_create(user=user, role=role)
                
                created.append({'id': user.id, 'username': username, 'real_name': real_name})
                
            except Exception as e:
                errors.append({'index': idx, 'error': str(e)})
        
        return Response({
            'created': created,
            'errors': errors,
            'total': len(teachers_data),
            'success_count': len(created),
            'error_count': len(errors)
        })
