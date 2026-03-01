from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import PartyBranch, PartyMember, PartyActivity
from .serializers import (
    PartyBranchSerializer, PartyMemberSerializer, PartyActivitySerializer
)

class PartyBranchViewSet(viewsets.ModelViewSet):
    """支部视图集"""
    queryset = PartyBranch.objects.all()
    serializer_class = PartyBranchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['branch_type', 'department']
    search_fields = ['name']

class PartyMemberViewSet(viewsets.ModelViewSet):
    """党员团员信息视图集"""
    queryset = PartyMember.objects.all()
    serializer_class = PartyMemberSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['member_type', 'branch']
    search_fields = ['user__real_name', 'user__username']

class PartyActivityViewSet(viewsets.ModelViewSet):
    """党团活动视图集"""
    queryset = PartyActivity.objects.all()
    serializer_class = PartyActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activity_type', 'branch']
    search_fields = ['title', 'content']

    @action(detail=True, methods=['post'])
    def sign_in(self, request, pk=None):
        """活动签到"""
        activity = self.get_object()
        user = request.user
        
        if activity.participants.filter(id=user.id).exists():
            return Response({'message': '已签到'}, status=status.HTTP_400_BAD_REQUEST)
            
        activity.participants.add(user)
        
        # 如果是志愿活动，增加用户志愿时长
        if activity.activity_type == 'volunteer' and activity.volunteer_hours_given > 0:
            party_info, created = PartyMember.objects.get_or_create(user=user)
            party_info.volunteer_hours = float(party_info.volunteer_hours) + float(activity.volunteer_hours_given)
            party_info.save()
            
        return Response({'message': '签到成功'})
