from django.contrib import admin
from .models import Course, CourseSelection, Grade


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'course_name', 'course_type', 'teacher', 'credits', 'capacity', 'enrolled_count', 'is_open']
    list_filter = ['course_type', 'is_open', 'is_active', 'department']
    search_fields = ['course_code', 'course_name', 'teacher__real_name']
    raw_id_fields = ['department', 'teacher']


@admin.register(CourseSelection)
class CourseSelectionAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'selection_time']
    list_filter = ['status', 'selection_time']
    search_fields = ['student__student_id', 'student__user__real_name', 'course__course_name']
    raw_id_fields = ['student', 'course']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'total_score', 'grade_point', 'semester', 'entered_by', 'is_confirmed']
    list_filter = ['grade_type', 'semester', 'is_confirmed', 'created_at']
    search_fields = ['student__student_id', 'student__user__real_name', 'course__course_name']
    raw_id_fields = ['student', 'course', 'entered_by']
