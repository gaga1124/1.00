from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import SocialPractice, Competition, CompetitionTeam, DynamicActivityType, DynamicActivityInstance
from .serializers import (
    SocialPracticeSerializer, CompetitionSerializer, CompetitionTeamSerializer,
    DynamicActivityTypeSerializer, DynamicActivityInstanceSerializer
)
from apps.workflow.models import Workflow, WorkflowNode, WorkflowInstance
from apps.workflow.views import WorkflowInstanceViewSet
from django.contrib.contenttypes.models import ContentType

class SocialPracticeViewSet(viewsets.ModelViewSet):
    """社会实践视图集"""
    queryset = SocialPractice.objects.all()
    serializer_class = SocialPracticeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'practice_type']
    search_fields = ['title', 'team_name', 'description']

    def perform_create(self, serializer):
        serializer.save(leader=self.request.user)

class CompetitionViewSet(viewsets.ModelViewSet):
    """学科竞赛视图集"""
    queryset = Competition.objects.filter(is_active=True)
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'organizer']

class CompetitionTeamViewSet(viewsets.ModelViewSet):
    """竞赛报名团队视图集"""
    queryset = CompetitionTeam.objects.all()
    serializer_class = CompetitionTeamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['competition', 'status']
    search_fields = ['team_name']

    def perform_create(self, serializer):
        team = serializer.save(leader=self.request.user)
        # 竞赛团队作品/活动发布：需指导教师审批
        wf, _ = Workflow.objects.get_or_create(
            code='WF_ACTIVITY_PUBLISH',
            defaults={'name': '活动发布审批', 'description': '发布组织对应的指导教师批准', 'created_by': self.request.user}
        )
        WorkflowNode.objects.get_or_create(
            workflow=wf, order=1,
            defaults={
                'name': '指导教师审批',
                'approver_type': 'user',
                # 使用条件表达式声明从业务对象字段取审批人
                'condition_expression': 'approver_field:advisor',
                'is_active': True
            }
        )
        instance = WorkflowInstance.objects.create(
            workflow=wf,
            title=f"竞赛报名/活动发布 - {team.team_name}",
            applicant=self.request.user,
            status='pending',
            current_node=None,
            content_type=ContentType.objects.get_for_model(team.__class__),
            object_id=team.id
        )
        # 初始化节点记录
        helper = WorkflowInstanceViewSet()
        helper.request = self.request
        first_node = helper._find_next_matching_node(instance, from_order=0)
        if first_node:
            instance.current_node = first_node
            instance.status = 'processing'
            instance.save()
            if not helper._create_node_records(instance, first_node):
                helper._auto_skip_node(instance, first_node)
                helper._move_to_next_node(instance)

    @action(detail=True, methods=['post'])
    def submit_work(self, request, pk=None):
        """提交参赛作品"""
        team = self.get_object()
        work_file = request.FILES.get('work_file')
        if not work_file:
            return Response({'error': '没有上传文件'}, status=400)
            
        team.work_file = work_file
        team.status = 'submitted'
        team.save()
        return Response({'message': '提交成功'})

class DynamicActivityTypeViewSet(viewsets.ModelViewSet):
    """动态活动类型视图集（仅管理员可管理）"""
    queryset = DynamicActivityType.objects.all()
    serializer_class = DynamicActivityTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class DynamicActivityInstanceViewSet(viewsets.ModelViewSet):
    """动态活动实例视图集"""
    queryset = DynamicActivityInstance.objects.all()
    serializer_class = DynamicActivityInstanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity_type', 'status']

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
