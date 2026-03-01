from django.contrib import admin
from .models import (
    ResearchProject, ProjectMilestone, ResearchAchievement,
    ResearchTeam, TeamTask, TeamMeeting
)


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ['project_code', 'project_name', 'project_type', 'principal', 'status', 'total_budget', 'used_budget']
    list_filter = ['project_type', 'status', 'created_at']
    search_fields = ['project_code', 'project_name', 'principal__real_name']
    raw_id_fields = ['principal']
    filter_horizontal = ['members']


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ['project', 'name', 'due_date', 'is_completed', 'completed_date']
    list_filter = ['is_completed', 'due_date']
    search_fields = ['project__project_name', 'name']
    raw_id_fields = ['project']


@admin.register(ResearchAchievement)
class ResearchAchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'achievement_type', 'first_author', 'journal', 'publish_date', 'is_verified']
    list_filter = ['achievement_type', 'is_verified', 'publish_date']
    search_fields = ['title', 'journal', 'first_author__real_name']
    raw_id_fields = ['project', 'first_author', 'verified_by']
    filter_horizontal = ['authors']


@admin.register(ResearchTeam)
class ResearchTeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'leader', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'leader__real_name']
    raw_id_fields = ['leader']
    filter_horizontal = ['members']


@admin.register(TeamTask)
class TeamTaskAdmin(admin.ModelAdmin):
    list_display = ['team', 'title', 'assignee', 'status', 'due_date']
    list_filter = ['status', 'due_date']
    search_fields = ['team__name', 'title', 'assignee__real_name']
    raw_id_fields = ['team', 'assignee']


@admin.register(TeamMeeting)
class TeamMeetingAdmin(admin.ModelAdmin):
    list_display = ['team', 'title', 'meeting_time', 'location', 'created_by']
    list_filter = ['meeting_time']
    search_fields = ['team__name', 'title']
    raw_id_fields = ['team', 'created_by']
    filter_horizontal = ['attendees']
