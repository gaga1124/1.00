"""
电子签章模块URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ElectronicFileViewSet, DepartmentSignatureViewSet, SignatureOperationLogViewSet

router = DefaultRouter()
router.register(r'files', ElectronicFileViewSet, basename='electronic_file')
router.register(r'signatures', DepartmentSignatureViewSet, basename='department_signature')
router.register(r'logs', SignatureOperationLogViewSet, basename='signature_log')

urlpatterns = [
    path('', include(router.urls)),
]
