from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, RoleViewSet, PermissionViewSet,
    RolePermissionViewSet, UserRoleViewSet, UserPositionViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'role-permissions', RolePermissionViewSet, basename='role-permission')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'user-positions', UserPositionViewSet, basename='user-position')

urlpatterns = [
    path('', include(router.urls)),
]
