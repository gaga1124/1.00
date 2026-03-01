from django.contrib import admin
from .models import Student, PoliticalStatusRecord, StudentRecord


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'department', 'counselor', 'major', 'class_name', 'political_status', 'created_at']
    list_filter = ['political_status', 'major', 'grade', 'department', 'created_at']
    search_fields = ['student_id', 'user__real_name', 'user__username', 'major', 'class_name', 'department__name', 'counselor__real_name']
    raw_id_fields = ['user', 'department', 'counselor']


@admin.register(PoliticalStatusRecord)
class PoliticalStatusRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'from_status', 'to_status', 'status', 'approver', 'created_at']
    list_filter = ['status', 'from_status', 'to_status', 'created_at']
    search_fields = ['student__student_id', 'student__user__real_name']
    raw_id_fields = ['student', 'approver']


@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'record_type', 'title', 'operator', 'created_at']
    list_filter = ['record_type', 'created_at']
    search_fields = ['student__student_id', 'student__user__real_name', 'title']
    raw_id_fields = ['student', 'operator']
