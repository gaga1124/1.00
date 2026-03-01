from django.contrib import admin
from .models import LeaveApplication, ReimbursementApplication, PartyMembershipApplication


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'leave_type', 'start_time', 'end_time', 'days', 'status', 'created_at']
    list_filter = ['leave_type', 'applicant_type', 'status', 'created_at']
    search_fields = ['applicant__real_name', 'applicant__username', 'reason']
    raw_id_fields = ['applicant', 'approver']


@admin.register(ReimbursementApplication)
class ReimbursementApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'category', 'title', 'amount', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['applicant__real_name', 'title', 'fund_card_number']
    raw_id_fields = ['applicant', 'approver']


@admin.register(PartyMembershipApplication)
class PartyMembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'application_type', 'status', 'current_step', 'created_at']
    list_filter = ['application_type', 'status', 'created_at']
    search_fields = ['student__student_id', 'student__user__real_name']
    raw_id_fields = ['student', 'approver']
