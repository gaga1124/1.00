from django.contrib import admin
from .models import Course, CourseSelection, Grade, StudentStatus


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'name', 'credit', 'teacher', 'semester', 'current_students', 'max_students', 'is_active']
    list_filter = ['course_type', 'semester', 'is_active', 'department']
    search_fields = ['course_code', 'name', 'teacher__real_name']
    raw_id_fields = ['department', 'teacher']


@admin.register(CourseSelection)
class CourseSelectionAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'selected_at']
    list_filter = ['status', 'selected_at']
    search_fields = ['student__student_id', 'student__user__real_name', 'course__name']
    raw_id_fields = ['student', 'course']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'score', 'grade_level', 'semester', 'teacher', 'recorded_at']
    list_filter = ['semester', 'grade_level', 'recorded_at']
    search_fields = ['student__student_id', 'student__user__real_name', 'course__name']
    raw_id_fields = ['student', 'course', 'teacher']


@admin.register(StudentStatus)
class StudentStatusAdmin(admin.ModelAdmin):
    list_display = ['student', 'status', 'student_type', 'admission_date', 'expected_graduation_date']
    list_filter = ['status', 'student_type', 'enrollment_type']
    search_fields = ['student__student_id', 'student__user__real_name']
    raw_id_fields = ['student']
