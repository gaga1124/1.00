from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db.models import Avg, Count, Sum, Q, F
from apps.academic.models import Grade, CourseSelection
from apps.career.models import EmploymentStatistics
from apps.research.models import ResearchProject, ResearchAchievement
from apps.students.models import Student
from django.utils import timezone

class DashboardStatsView(APIView):
    """大屏数据统计接口"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. 教学质量分析
        avg_score = Grade.objects.aggregate(Avg('score'))['score__avg'] or 0
        fail_rate = Grade.objects.filter(score__lt=60).count() / max(Grade.objects.count(), 1)
        
        # 2. 就业率统计
        total_graduates = EmploymentStatistics.objects.count()
        employed_count = EmploymentStatistics.objects.filter(is_employed=True).count()
        employment_rate = (employed_count / max(total_graduates, 1)) * 100
        
        # 3. 科研成果统计
        total_projects = ResearchProject.objects.count()
        total_achievements = ResearchAchievement.objects.count()
        total_funds = ResearchProject.objects.aggregate(Sum('total_budget'))['total_budget__sum'] or 0
        
        return Response({
            'academic': {
                'avg_score': round(float(avg_score), 2),
                'fail_rate': round(fail_rate * 100, 2),
            },
            'employment': {
                'total_graduates': total_graduates,
                'employed_count': employed_count,
                'employment_rate': round(employment_rate, 2),
            },
            'research': {
                'total_projects': total_projects,
                'total_achievements': total_achievements,
                'total_funds': float(total_funds),
            }
        })

class WarningSystemView(APIView):
    """预警功能接口"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        warnings = []
        
        # 1. 挂科率过高预警 (单门课程挂科率超过20%)
        course_fails = Grade.objects.values('course__name').annotate(
            total=Count('id'),
            fails=Count('id', filter=Q(score__lt=60))
        )
        for cf in course_fails:
            if cf['total'] > 5 and (cf['fails'] / cf['total']) > 0.2:
                warnings.append({
                    'type': 'academic',
                    'level': 'high',
                    'message': f"课程 [{cf['course__name']}] 挂科率异常: {round(cf['fails']/cf['total']*100, 2)}%"
                })
        
        # 2. 经费超支预警
        over_budget_projects = ResearchProject.objects.filter(used_budget__gt=F('total_budget'))
        for p in over_budget_projects:
            warnings.append({
                'type': 'research',
                'level': 'medium',
                'message': f"项目 [{p.project_name}] 经费已超支"
            })
            
        return Response(warnings)

class DecisionSupportView(APIView):
    """决策建议接口"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 基于历史数据的趋势分析示例
        # 1. 热门专业预测 (基于选课人数)
        hot_majors = CourseSelection.objects.values('student__major').annotate(
            selection_count=Count('id')
        ).order_by('-selection_count')[:5]
        
        return Response({
            'trend_analysis': {
                'hot_majors': hot_majors,
                'suggestion': "建议根据选课趋势调整下一年度专业招生规模计划。"
            }
        })
