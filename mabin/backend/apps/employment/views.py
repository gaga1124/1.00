from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.db import transaction
from .models import Company, JobPosting, JobApplication, JobFair, JobFairRegistration, EmploymentStatistics
from .serializers import (
    CompanySerializer, JobPostingSerializer, JobApplicationSerializer,
    JobFairSerializer, JobFairRegistrationSerializer, EmploymentStatisticsSerializer
)


class CompanyViewSet(viewsets.ModelViewSet):
    """企业视图集"""
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]


class JobPostingViewSet(viewsets.ModelViewSet):
    """招聘信息视图集"""
    queryset = JobPosting.objects.filter(is_active=True)
    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """投递简历"""
        job_posting = self.get_object()
        student = request.user.student_profile
        
        if not student:
            return Response({'error': '当前用户不是学生'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已投递
        if JobApplication.objects.filter(student=student, job_posting=job_posting).exists():
            return Response({'error': '您已投递过此职位'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建投递记录
        with transaction.atomic():
            application = JobApplication.objects.create(
                student=student,
                job_posting=job_posting,
                resume=request.data.get('resume'),
                cover_letter=request.data.get('cover_letter', '')
            )
            job_posting.applied_count += 1
            job_posting.save()
        
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """招聘数据统计"""
        total_postings = JobPosting.objects.filter(is_active=True).count()
        total_applications = JobApplication.objects.count()
        active_companies = Company.objects.filter(is_active=True, is_verified=True).count()
        
        return Response({
            'total_postings': total_postings,
            'total_applications': total_applications,
            'active_companies': active_companies,
            'average_applications_per_posting': round(total_applications / total_postings, 2) if total_postings > 0 else 0
        })


class JobApplicationViewSet(viewsets.ModelViewSet):
    """简历投递视图集"""
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
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
        
        # 企业可以看到自己职位的投递
        # TODO: 实现企业用户权限
        
        return queryset.none()


class JobFairViewSet(viewsets.ModelViewSet):
    """招聘会视图集"""
    queryset = JobFair.objects.filter(is_active=True)
    serializer_class = JobFairSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """报名招聘会"""
        job_fair = self.get_object()
        student = request.user.student_profile
        
        if not student:
            return Response({'error': '当前用户不是学生'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已报名
        if JobFairRegistration.objects.filter(student=student, job_fair=job_fair).exists():
            return Response({'error': '您已报名此招聘会'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查报名时间
        now = timezone.now()
        if job_fair.registration_start > now or job_fair.registration_end < now:
            return Response({'error': '不在报名时间内'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查容量
        if job_fair.capacity > 0 and job_fair.registered_count >= job_fair.capacity:
            return Response({'error': '招聘会已满'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建报名记录
        with transaction.atomic():
            registration = JobFairRegistration.objects.create(
                student=student,
                job_fair=job_fair
            )
            job_fair.registered_count += 1
            job_fair.save()
        
        serializer = JobFairRegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class JobFairRegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    """招聘会报名视图集（只读）"""
    queryset = JobFairRegistration.objects.all()
    serializer_class = JobFairRegistrationSerializer
    permission_classes = [IsAuthenticated]


class EmploymentStatisticsViewSet(viewsets.ModelViewSet):
    """就业数据视图集"""
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
        graduation_year = request.query_params.get('graduation_year')
        department_id = request.query_params.get('department_id')
        
        queryset = self.get_queryset()
        
        if graduation_year:
            queryset = queryset.filter(graduation_year=graduation_year)
        if department_id:
            queryset = queryset.filter(student__user__department_id=department_id)
        
        total = queryset.count()
        employed = queryset.filter(is_employed=True).count()
        employment_rate = round(employed / total * 100, 2) if total > 0 else 0
        
        # 就业类型统计
        employment_types = queryset.filter(is_employed=True).values('employment_type').annotate(
            count=Count('id')
        )
        
        # 平均薪资
        avg_salary = queryset.filter(is_employed=True, salary__isnull=False).aggregate(
            avg=Avg('salary')
        )['avg'] or 0
        
        # 专业对口率
        major_match_count = queryset.filter(is_employed=True, major_match=True).count()
        major_match_rate = round(major_match_count / employed * 100, 2) if employed > 0 else 0
        
        return Response({
            'total': total,
            'employed': employed,
            'employment_rate': employment_rate,
            'employment_types': list(employment_types),
            'average_salary': float(avg_salary),
            'major_match_rate': major_match_rate
        })
