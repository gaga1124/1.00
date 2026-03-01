from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.students.serializers import StudentSerializer
from apps.rbac.serializers import DepartmentSerializer
from .models import Course, CourseSelection, Grade, Assignment, AssignmentSubmission


class CourseSerializer(serializers.ModelSerializer):
    """课程序列化器"""
    teacher_name = serializers.CharField(source='teacher.real_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    is_full = serializers.SerializerMethodField()
    can_select = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'course_name', 'course_type', 'course_type_display',
            'department', 'department_name', 'teacher', 'teacher_name',
            'credits', 'hours', 'capacity', 'enrolled_count', 'is_full',
            'classroom', 'schedule', 'description', 'syllabus',
            'is_open', 'can_select', 'start_time', 'end_time',
            'assessment_method', 'score_composition',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'enrolled_count', 'created_at', 'updated_at']
    
    def get_is_full(self, obj):
        return obj.enrolled_count >= obj.capacity if obj.capacity > 0 else False
    
    def get_can_select(self, obj):
        from django.utils import timezone
        if not obj.is_open:
            return False
        if obj.capacity > 0 and obj.enrolled_count >= obj.capacity:
            return False
        if obj.start_time and timezone.now() < obj.start_time:
            return False
        if obj.end_time and timezone.now() > obj.end_time:
            return False
        return True


class CourseSelectionSerializer(serializers.ModelSerializer):
    """选课记录序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CourseSelection
        fields = [
            'id', 'student', 'student_name', 'student_id',
            'course', 'course_name', 'course_code',
            'status', 'status_display', 'selection_time', 'drop_time', 'reason'
        ]
        read_only_fields = ['id', 'selection_time']


class GradeSerializer(serializers.ModelSerializer):
    """成绩序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    entered_by_name = serializers.CharField(source='entered_by.real_name', read_only=True)
    grade_type_display = serializers.CharField(source='get_grade_type_display', read_only=True)
    
    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_name', 'student_id',
            'course', 'course_name', 'course_code',
            'usual_score', 'midterm_score', 'final_score', 'total_score',
            'grade_point', 'grade_level', 'grade_type', 'grade_type_display',
            'semester', 'academic_year',
            'entered_by', 'entered_by_name', 'entered_at', 'is_confirmed',
            'remark', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'entered_at', 'created_at', 'updated_at']


class AssignmentSerializer(serializers.ModelSerializer):
    """作业序列化器"""
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    student_status = serializers.SerializerMethodField() # 学生视角的转态
    submission_count = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_student_status(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request.user, 'student_profile'):
            return None
        
        # 查找最新的提交
        submission = obj.submissions.filter(student=request.user.student_profile).first()
        if submission:
            return submission.status
        
        # Check overdue
        from django.utils import timezone
        if timezone.now() > obj.deadline:
            return 'overdue' # 逾期未交
        
        return 'pending' # 待提交

    def get_submission_count(self, obj):
        return obj.submissions.count()

    def get_total_students(self, obj):
        return obj.course.enrolled_count


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """作业提交序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AssignmentSubmission
        fields = '__all__'
        read_only_fields = [
            'id', 'student', 'submitted_at', 'is_late', 
            'score', 'feedback', 'status'
        ] 
        # 注意：student 是自动设置的，student不能改
        # score/feedback 是老师改的
