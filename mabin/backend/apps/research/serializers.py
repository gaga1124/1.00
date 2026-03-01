from rest_framework import serializers
from .models import (
    ResearchProject, ProjectMilestone, ResearchAchievement,
    ResearchTeam, TeamTask, TeamMeeting
)
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'avatar']

class ProjectMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMilestone
        fields = '__all__'

class ResearchProjectSerializer(serializers.ModelSerializer):
    principal_info = UserSimpleSerializer(source='principal', read_only=True)
    members_info = UserSimpleSerializer(source='members', many=True, read_only=True)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)
    
    class Meta:
        model = ResearchProject
        fields = '__all__'
        read_only_fields = ['principal', 'created_at', 'updated_at']

class ResearchAchievementSerializer(serializers.ModelSerializer):
    authors_info = UserSimpleSerializer(source='authors', many=True, read_only=True)
    first_author_info = UserSimpleSerializer(source='first_author', read_only=True)
    
    class Meta:
        model = ResearchAchievement
        fields = '__all__'
        read_only_fields = ['authors', 'first_author', 'verified_by', 'verified_at', 'created_at']

class TeamTaskSerializer(serializers.ModelSerializer):
    assignee_info = UserSimpleSerializer(source='assignee', read_only=True)
    
    class Meta:
        model = TeamTask
        fields = '__all__'

class TeamMeetingSerializer(serializers.ModelSerializer):
    attendees_info = UserSimpleSerializer(source='attendees', many=True, read_only=True)
    
    class Meta:
        model = TeamMeeting
        fields = '__all__'

class ResearchTeamSerializer(serializers.ModelSerializer):
    leader_info = UserSimpleSerializer(source='leader', read_only=True)
    members_info = UserSimpleSerializer(source='members', many=True, read_only=True)
    tasks = TeamTaskSerializer(many=True, read_only=True)
    meetings = TeamMeetingSerializer(many=True, read_only=True)
    
    class Meta:
        model = ResearchTeam
        fields = '__all__'
