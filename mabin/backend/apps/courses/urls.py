from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, CourseSelectionViewSet, GradeViewSet,
    AssignmentViewSet, AssignmentSubmissionViewSet
)

router = DefaultRouter()
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'submissions', AssignmentSubmissionViewSet, basename='assignment-submission')
router.register(r'selections', CourseSelectionViewSet, basename='course-selection')
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
]
