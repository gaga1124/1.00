from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.students.serializers import StudentSerializer
from apps.rbac.serializers import DepartmentSerializer
from .models import Course, CourseSelection, Grade, StudentStatus, AttendanceSession, Attendance, Assignment, AssignmentSubmission


class CourseSerializer(serializers.ModelSerializer):
    """课程序列化器"""
    teacher_name = serializers.CharField(source='teacher.real_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    is_full = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'name', 'credit', 'hours', 'course_type', 'course_type_display',
            'assessment_method',
            'department', 'department_name', 'teacher', 'teacher_name', 'description',
            'max_students', 'current_students', 'is_full', 'semester', 'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'current_students', 'created_at']
    
    def get_is_full(self, obj):
        return obj.current_students >= obj.max_students


class CourseSelectionSerializer(serializers.ModelSerializer):
    """选课记录序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CourseSelection
        fields = [
            'id', 'student', 'student_name', 'student_id', 'course', 'course_name',
            'course_code', 'status', 'status_display', 'selected_at', 'dropped_at'
        ]
        read_only_fields = ['id', 'selected_at', 'dropped_at']


class GradeSerializer(serializers.ModelSerializer):
    """成绩序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    teacher_name = serializers.CharField(source='teacher.real_name', read_only=True)
    grade_level_display = serializers.CharField(source='get_grade_level_display', read_only=True)
    
    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_name', 'student_id', 'course', 'course_name', 'course_code',
            'score', 'grade_point', 'grade_level', 'grade_level_display', 'semester',
            'teacher', 'teacher_name', 'recorded_at', 'updated_at', 'remark'
        ]
        read_only_fields = ['id', 'recorded_at', 'updated_at']


class StudentStatusSerializer(serializers.ModelSerializer):
    """学籍状态序列化器"""
    student_info = StudentSerializer(source='student', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    student_type_display = serializers.CharField(source='get_student_type_display', read_only=True)
    enrollment_type_display = serializers.CharField(source='get_enrollment_type_display', read_only=True)
    
    class Meta:
        model = StudentStatus
        fields = [
            'id', 'student', 'student_info', 'status', 'status_display',
            'admission_date', 'expected_graduation_date', 'actual_graduation_date',
            'student_type', 'student_type_display', 'enrollment_type', 'enrollment_type_display',
            'status_changes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AttendanceSessionSerializer(serializers.ModelSerializer):
    """签到会话序列化器"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.real_name', read_only=True)
    present_count = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceSession
        fields = [
            'id', 'course', 'course_name', 'teacher', 'teacher_name',
            'date', 'time_slot', 'check_in_code', 'is_active', 'expire_at',
            'present_count', 'total_count', 'created_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at']

    def get_present_count(self, obj):
        return obj.records.filter(status='present').count()

    def get_total_count(self, obj):
        return obj.course.current_students


class AttendanceSerializer(serializers.ModelSerializer):
    """课堂签到序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    session_info = AttendanceSessionSerializer(source='session', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'session', 'session_info', 'student', 'student_name', 'student_id',
            'course', 'course_name', 'date', 'time_slot', 'status', 'status_display',
            'remark', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AssignmentSerializer(serializers.ModelSerializer):
    """作业序列化器"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    submission_count = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    student_status = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'course', 'course_name', 'title', 'description', 'deadline',
            'allow_late_submission', 'late_penalty', 'weight_in_score', 'file',
            'submission_count', 'total_students', 'student_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_submission_count(self, obj):
        return obj.submissions.count()

    def get_total_students(self, obj):
        return obj.course.current_students

    def get_student_status(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student_profile'):
            submission = obj.submissions.filter(student=request.user.student_profile).first()
            return submission.status if submission else 'pending'
        return None


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """作业提交序列化器"""
    student_name = serializers.CharField(source='student.user.real_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'assignment_title', 'student', 'student_name', 'student_id',
            'file', 'content', 'submitted_at', 'is_late', 'score', 'feedback', 'status', 'status_display'
        ]
        read_only_fields = ['id', 'submitted_at', 'is_late']
