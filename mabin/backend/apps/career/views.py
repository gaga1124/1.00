from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.db import transaction
from .models import (
    Company, JobPosting, Resume, JobApplication,
    JobFair, JobFairRegistration, EmploymentStatistics
)
from .serializers import (
    CompanySerializer, JobPostingSerializer, ResumeSerializer,
    JobApplicationSerializer, JobFairSerializer, EmploymentStatisticsSerializer
)


class CompanyViewSet(viewsets.ModelViewSet):
    """企业视图集"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]


class JobPostingViewSet(viewsets.ModelViewSet):
    """招聘信息视图集"""
    queryset = JobPosting.objects.filter(is_active=True)
    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """查看招聘信息（增加浏览次数）"""
        job = self.get_object()
        job.views_count += 1
        job.save()
        return Response({'views_count': job.views_count})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """招聘统计"""
        total_jobs = self.get_queryset().count()
        by_type = self.get_queryset().values('job_type').annotate(count=Count('id'))
        by_industry = JobPosting.objects.filter(
            is_active=True
        ).values('company__industry').annotate(count=Count('id'))
        
        return Response({
            'total_jobs': total_jobs,
            'by_type': list(by_type),
            'by_industry': list(by_industry)
        })


class ResumeViewSet(viewsets.ModelViewSet):
    """简历视图集"""
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """学生只能看自己的简历"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        if hasattr(user, 'student_profile'):
            return queryset.filter(student=user.student_profile)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """创建简历时自动关联学生"""
        if hasattr(self.request.user, 'student_profile'):
            serializer.save(student=self.request.user.student_profile)
        else:
            raise serializers.ValidationError('非学生用户无法创建简历')


class JobApplicationViewSet(viewsets.ModelViewSet):
    """职位申请视图集"""
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据用户角色过滤"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        # 学生只能看自己的申请
        if hasattr(user, 'student_profile'):
            return queryset.filter(student=user.student_profile)
        
        # 企业可以看自己职位的申请
        return queryset.filter(job__company__contact_email=user.email)
    
    @transaction.atomic
    def perform_create(self, serializer):
        """申请职位"""
        if not hasattr(self.request.user, 'student_profile'):
            raise serializers.ValidationError('非学生用户无法申请职位')
        
        job = serializer.validated_data['job']
        student = self.request.user.student_profile
        
        # 检查是否已申请
        if JobApplication.objects.filter(job=job, student=student).exists():
            raise serializers.ValidationError('已申请过该职位')
        
        serializer.save(student=student)


class JobFairViewSet(viewsets.ModelViewSet):
    """招聘会视图集"""
    queryset = JobFair.objects.filter(is_active=True)
    serializer_class = JobFairSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """报名招聘会"""
        job_fair = self.get_object()
        
        if not hasattr(request.user, 'student_profile'):
            return Response({'error': '非学生用户无法报名'}, status=status.HTTP_400_BAD_REQUEST)
        
        student = request.user.student_profile
        
        # 检查是否已报名
        if JobFairRegistration.objects.filter(job_fair=job_fair, student=student).exists():
            return Response({'error': '已报名'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已满
        if job_fair.current_participants >= job_fair.max_participants:
            return Response({'error': '报名已满'}, status=status.HTTP_400_BAD_REQUEST)
        
        JobFairRegistration.objects.create(job_fair=job_fair, student=student)
        
        # 更新报名人数
        job_fair.current_participants += 1
        job_fair.save()
        
        return Response({'message': '报名成功'})


class EmploymentStatisticsViewSet(viewsets.ModelViewSet):
    """就业统计视图集"""
    queryset = EmploymentStatistics.objects.all()
    serializer_class = EmploymentStatisticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据用户角色过滤"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        # 学生只能看自己的
        if hasattr(user, 'student_profile'):
            return queryset.filter(student=user.student_profile)
        
        # 学院秘书可以看本学院的
        if user.department:
            return queryset.filter(student__user__department=user.department)
        
        return queryset.none()
    
    @action(detail=False, methods=['get'])
    def analysis(self, request):
        """就业数据分析"""
        queryset = self.get_queryset()
        
        # 就业率
        total = queryset.count()
        employed = queryset.filter(employment_status='employed').count()
        employment_rate = round(employed / total * 100, 2) if total > 0 else 0
        
        # 就业去向（按行业）
        by_industry = queryset.filter(
            employment_status='employed'
        ).values('company__industry').annotate(count=Count('id'))
        
        # 平均薪资
        avg_salary = queryset.filter(
            employment_status='employed',
            salary__isnull=False
        ).aggregate(Avg('salary'))['salary__avg']
        
        # 就业来源
        by_source = queryset.values('source').annotate(count=Count('id'))
        
        return Response({
            'employment_rate': employment_rate,
            'by_industry': list(by_industry),
            'avg_salary': round(avg_salary, 2) if avg_salary else 0,
            'by_source': list(by_source)
        })
