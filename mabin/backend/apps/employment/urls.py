from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet, JobPostingViewSet, JobApplicationViewSet,
    JobFairViewSet, JobFairRegistrationViewSet, EmploymentStatisticsViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'postings', JobPostingViewSet, basename='job-posting')
router.register(r'applications', JobApplicationViewSet, basename='job-application')
router.register(r'fairs', JobFairViewSet, basename='job-fair')
router.register(r'fair-registrations', JobFairRegistrationViewSet, basename='job-fair-registration')
router.register(r'statistics', EmploymentStatisticsViewSet, basename='employment-statistics')

urlpatterns = [
    path('', include(router.urls)),
]
