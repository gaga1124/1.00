from django.contrib import admin
from .models import SocialPractice, Competition, CompetitionTeam, DynamicActivityType, DynamicActivityInstance

@admin.register(SocialPractice)
class SocialPracticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'practice_type', 'leader', 'status', 'created_at')
    list_filter = ('status', 'practice_type')
    search_fields = ('title', 'team_name')

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'organizer', 'registration_deadline', 'is_active')
    list_filter = ('level', 'is_active')

@admin.register(CompetitionTeam)
class CompetitionTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'competition', 'leader', 'status', 'score', 'award_level')
    list_filter = ('status', 'award_level')

@admin.register(DynamicActivityType)
class DynamicActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    search_fields = ('name', 'code')

@admin.register(DynamicActivityInstance)
class DynamicActivityInstanceAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'creator', 'status', 'created_at')
    list_filter = ('activity_type', 'status')
