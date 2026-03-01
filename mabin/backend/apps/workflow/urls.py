from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkflowViewSet, WorkflowNodeViewSet,
    WorkflowInstanceViewSet, WorkflowInstanceNodeViewSet
)

router = DefaultRouter()
router.register(r'nodes', WorkflowNodeViewSet, basename='workflow-node')
router.register(r'instances', WorkflowInstanceViewSet, basename='workflow-instance')
router.register(r'instance-nodes', WorkflowInstanceNodeViewSet, basename='workflow-instance-node')
router.register(r'', WorkflowViewSet, basename='workflow')

urlpatterns = [
    path('', include(router.urls)),
]
