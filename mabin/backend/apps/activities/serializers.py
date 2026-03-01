from rest_framework import serializers
from .models import SocialPractice, Competition, CompetitionTeam, DynamicActivityType, DynamicActivityInstance
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'avatar']

class SocialPracticeSerializer(serializers.ModelSerializer):
    leader_info = UserSimpleSerializer(source='leader', read_only=True)
    members_info = UserSimpleSerializer(source='members', many=True, read_only=True)
    
    class Meta:
        model = SocialPractice
        fields = '__all__'

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'

class CompetitionTeamSerializer(serializers.ModelSerializer):
    leader_info = UserSimpleSerializer(source='leader', read_only=True)
    members_info = UserSimpleSerializer(source='members', many=True, read_only=True)
    advisor_info = UserSimpleSerializer(source='advisor', read_only=True)
    competition_name = serializers.CharField(source='competition.title', read_only=True)
    
    class Meta:
        model = CompetitionTeam
        fields = '__all__'

class DynamicActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicActivityType
        fields = '__all__'

class DynamicActivityInstanceSerializer(serializers.ModelSerializer):
    creator_info = UserSimpleSerializer(source='creator', read_only=True)
    type_name = serializers.CharField(source='activity_type.name', read_only=True)
    
    class Meta:
        model = DynamicActivityInstance
        fields = '__all__'
