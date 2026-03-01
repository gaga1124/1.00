from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.users.models import UserProfile
from .models import Student, PoliticalStatusRecord, StudentRecord, StudentStatusChange, ArchiveViewLog


class StudentSerializer(serializers.ModelSerializer):
    """学生序列化器"""
    user_info = UserSerializer(source='user', read_only=True)
    political_status_display = serializers.CharField(source='get_political_status_display', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    counselor_name = serializers.CharField(source='counselor.real_name', read_only=True)
    
    # 档案相关（仅在详情时提供或按需包含）
    political_records = serializers.SerializerMethodField()
    status_changes = serializers.SerializerMethodField()
    archive_records = serializers.SerializerMethodField()
    
    # 自定义字段，用于接收前端输入和返回数据
    real_name = serializers.CharField(label='姓名', required=False)
    id_card = serializers.CharField(label='身份证号', required=False, allow_blank=True)
    phone = serializers.CharField(label='手机号', required=False, allow_blank=True)
    email = serializers.EmailField(label='邮箱', required=False, allow_blank=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'user_info', 'student_id', 'major', 'class_name', 'grade',
            'department', 'department_name', 'counselor', 'counselor_name',
            'political_status', 'political_status_display', 'photo', 'extra_data',
            'political_records', 'status_changes', 'archive_records',
            'created_at', 'updated_at', 'real_name', 'id_card', 'phone', 'email'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def get_political_records(self, obj):
        if self.context.get('include_details'):
            return PoliticalStatusRecordSerializer(obj.political_status_records.all()[:10], many=True).data
        return []

    def get_status_changes(self, obj):
        if self.context.get('include_details'):
            return StudentStatusChangeSerializer(obj.status_changes.all()[:10], many=True).data
        return []

    def get_archive_records(self, obj):
        if self.context.get('include_details'):
            return StudentRecordSerializer(obj.records.all()[:10], many=True).data
        return []

    def to_representation(self, instance):
        """自定义返回数据，填充姓名和身份证号"""
        ret = super().to_representation(instance)
        if instance.user:
            ret['real_name'] = instance.user.real_name
            ret['id_card'] = instance.user.id_card
            ret['phone'] = instance.user.phone
            ret['email'] = instance.user.email
        return ret

    def create(self, validated_data):
        """创建学生时自动创建用户"""
        real_name = validated_data.pop('real_name', '')
        id_card = validated_data.pop('id_card', '')
        phone = validated_data.pop('phone', '')
        email = validated_data.pop('email', '')
        student_id = validated_data.get('student_id')
        department = validated_data.get('department', None)
        
        # 自动创建用户
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # 检查用户是否已存在
        if User.objects.filter(username=student_id).exists():
             raise serializers.ValidationError({'student_id': '该学号已对应的用户已存在'})
             
        user = User.objects.create_user(
            username=student_id,
            password=student_id, # 默认密码为学号
            real_name=real_name,
            id_card=id_card,
            phone=phone,
            email=email
        )
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'employee_id': student_id
            }
        )
        # 同步用户的学院/部门，便于统一按 user.department 进行过滤和审批
        if department:
            try:
                user.department = department
                user.save(update_fields=['department'])
            except Exception:
                pass
        
        # 赋予学生角色
        from apps.rbac.models import Role, UserRole
        student_role = Role.objects.filter(code='student').first()
        if student_role:
            UserRole.objects.create(user=user, role=student_role)
            
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """更新学生信息时同步更新用户"""
        real_name = validated_data.pop('real_name', None)
        id_card = validated_data.pop('id_card', None)
        phone = validated_data.pop('phone', None)
        email = validated_data.pop('email', None)
        
        if instance.user:
            if real_name is not None:
                instance.user.real_name = real_name
            if id_card is not None:
                instance.user.id_card = id_card
            if phone is not None:
                instance.user.phone = phone
            if email is not None:
                instance.user.email = email
                
            if any(x is not None for x in [real_name, id_card, phone, email]):
                instance.user.save()
            
        return super().update(instance, validated_data)


class StudentStatusChangeSerializer(serializers.ModelSerializer):
    """学籍变动记录序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    operator_name = serializers.CharField(source='operator.real_name', read_only=True)
    
    class Meta:
        model = StudentStatusChange
        fields = [
            'id', 'student', 'student_name', 'student_id',
            'change_type', 'change_type_display', 'from_status', 'to_status',
            'reason', 'change_date', 'document_no', 'attachments',
            'operator', 'operator_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PoliticalStatusRecordSerializer(serializers.ModelSerializer):
    """政治面貌流转记录序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    from_status_display = serializers.CharField(source='get_from_status_display', read_only=True)
    to_status_display = serializers.CharField(source='get_to_status_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approver_name = serializers.CharField(source='approver.real_name', read_only=True)
    
    class Meta:
        model = PoliticalStatusRecord
        fields = [
            'id', 'student', 'student_name', 'student_id',
            'from_status', 'from_status_display', 'to_status', 'to_status_display',
            'application_date', 'approval_date', 'status', 'status_display',
            'application_file', 'thought_report', 'other_materials',
            'approver', 'approver_name', 'approval_comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ArchiveViewLogSerializer(serializers.ModelSerializer):
    """档案查阅日志序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    viewer_name = serializers.CharField(source='viewer.real_name', read_only=True)
    
    class Meta:
        model = ArchiveViewLog
        fields = [
            'id', 'student', 'student_name', 'student_id',
            'viewer', 'viewer_name', 'reason', 'ip_address', 'viewed_at'
        ]
        read_only_fields = ['id', 'viewed_at']


class StudentRecordSerializer(serializers.ModelSerializer):
    """学生档案记录序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    operator_name = serializers.CharField(source='operator.real_name', read_only=True)
    
    class Meta:
        model = StudentRecord
        fields = [
            'id', 'student', 'student_name', 'student_id',
            'record_type', 'record_type_display', 'title', 'description',
            'record_data', 'attachments', 'operator', 'operator_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
