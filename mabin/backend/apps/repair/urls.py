from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RepairCategoryViewSet, RepairApplicationViewSet, RepairRecordViewSet
)

router = DefaultRouter()
router.register(r'categories', RepairCategoryViewSet, basename='repair-category')
router.register(r'applications', RepairApplicationViewSet, basename='repair-application')
router.register(r'records', RepairRecordViewSet, basename='repair-record')

urlpatterns = [
    path('', include(router.urls)),
]
