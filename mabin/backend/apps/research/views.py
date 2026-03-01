from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Sum
from .models import (
    ResearchProject, ProjectMilestone, ResearchAchievement,
    ResearchTeam, TeamTask, TeamMeeting
)
from .serializers import (
    ResearchProjectSerializer, ProjectMilestoneSerializer,
    ResearchAchievementSerializer, ResearchTeamSerializer,
    TeamTaskSerializer, TeamMeetingSerializer
)

class ResearchProjectViewSet(viewsets.ModelViewSet):
    """科研项目视图集"""
    queryset = ResearchProject.objects.all()
    serializer_class = ResearchProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project_type', 'status', 'principal']
    search_fields = ['project_code', 'project_name', 'description']
    
    def perform_create(self, serializer):
        serializer.save(principal=self.request.user)
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user, 'has_role', None) and user.has_role('research_admin'):
            return self.queryset
        return self.queryset.filter(
            models.Q(principal=user) | models.Q(members=user)
        ).distinct()

    @action(detail=True, methods=['post'])
    def update_budget(self, request, pk=None):
        """更新经费使用情况"""
        project = self.get_object()
        category = request.data.get('category')
        amount = request.data.get('amount')
        
        if not (project.principal_id == request.user.id or request.user.is_superuser or (getattr(request.user, 'has_role', None) and request.user.has_role('research_admin'))):
            return Response({'error': '无权操作'}, status=403)
        
        if not category or not amount:
            return Response({'error': '必须提供类别和金额'}, status=400)
            
        # 更新经费明细
        details = project.budget_details or []
        found = False
        for item in details:
            if item['category'] == category:
                item['used'] = float(item.get('used', 0)) + float(amount)
                found = True
                break
        if not found:
            details.append({'category': category, 'amount': 0, 'used': float(amount)})
            
        project.budget_details = details
        project.used_budget = sum(float(item.get('used', 0)) for item in details)
        project.save()
        
        return Response(self.get_serializer(project).data)

class ResearchAchievementViewSet(viewsets.ModelViewSet):
    """科研成果视图集"""
    queryset = ResearchAchievement.objects.all()
    serializer_class = ResearchAchievementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['achievement_type', 'is_verified']
    search_fields = ['title', 'journal', 'doi']

    def perform_create(self, serializer):
        achievement = serializer.save(first_author=self.request.user)
        achievement.authors.add(self.request.user)

class ResearchTeamViewSet(viewsets.ModelViewSet):
    """科研团队视图集"""
    queryset = ResearchTeam.objects.all()
    serializer_class = ResearchTeamSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        team = self.get_object()
        user_id = request.data.get('user_id')
        if user_id:
            team.members.add(user_id)
            return Response({'status': 'member added'})
        return Response({'error': 'user_id required'}, status=400)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        team = self.get_object()
        user_id = request.data.get('user_id')
        if user_id:
            if user_id == team.leader_id:
                return Response({'error': 'Cannot remove leader from team'}, status=400)
            team.members.remove(user_id)
            return Response({'status': 'member removed'})
        return Response({'error': 'user_id required'}, status=400)

class TeamTaskViewSet(viewsets.ModelViewSet):
    """团队任务视图集"""
    queryset = TeamTask.objects.all()
    serializer_class = TeamTaskSerializer
    permission_classes = [IsAuthenticated]

class TeamMeetingViewSet(viewsets.ModelViewSet):
    """团队会议视图集"""
    queryset = TeamMeeting.objects.all()
    serializer_class = TeamMeetingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
