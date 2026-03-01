from rest_framework import serializers
from .models import PartyBranch, PartyMember, PartyActivity
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'avatar']

class PartyBranchSerializer(serializers.ModelSerializer):
    secretary_info = UserSimpleSerializer(source='secretary', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = PartyBranch
        fields = '__all__'

class PartyMemberSerializer(serializers.ModelSerializer):
    user_info = UserSimpleSerializer(source='user', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = PartyMember
        fields = '__all__'

class PartyActivitySerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    participants_info = UserSimpleSerializer(source='participants', many=True, read_only=True)
    
    class Meta:
        model = PartyActivity
        fields = '__all__'
