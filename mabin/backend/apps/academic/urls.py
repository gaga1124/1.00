from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, CourseSelectionViewSet, GradeViewSet, StudentStatusViewSet, 
    AttendanceSessionViewSet, AttendanceViewSet, AssignmentViewSet, AssignmentSubmissionViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'selections', CourseSelectionViewSet, basename='course-selection')
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'student-status', StudentStatusViewSet, basename='student-status')
router.register(r'attendance-sessions', AttendanceSessionViewSet, basename='attendance-session')
router.register(r'attendances', AttendanceViewSet, basename='attendance')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'submissions', AssignmentSubmissionViewSet, basename='assignment-submission')

urlpatterns = [
    path('', include(router.urls)),
]
