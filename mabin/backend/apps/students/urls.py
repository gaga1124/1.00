from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet, PoliticalStatusRecordViewSet, StudentRecordViewSet,
    StudentStatusChangeViewSet, ArchiveViewLogViewSet
)

router = DefaultRouter()
router.register(r'political-records', PoliticalStatusRecordViewSet, basename='political-record')
router.register(r'status-changes', StudentStatusChangeViewSet, basename='student-status-change')
router.register(r'records', StudentRecordViewSet, basename='student-record')
router.register(r'view-logs', ArchiveViewLogViewSet, basename='archive-view-log')
router.register(r'', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
]
