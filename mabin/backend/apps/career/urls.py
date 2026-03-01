from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet, JobPostingViewSet, ResumeViewSet,
    JobApplicationViewSet, JobFairViewSet, EmploymentStatisticsViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'jobs', JobPostingViewSet, basename='job-posting')
router.register(r'resumes', ResumeViewSet, basename='resume')
router.register(r'applications', JobApplicationViewSet, basename='job-application')
router.register(r'job-fairs', JobFairViewSet, basename='job-fair')
router.register(r'statistics', EmploymentStatisticsViewSet, basename='employment-statistics')

urlpatterns = [
    path('', include(router.urls)),
]
