from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileViewSet, TeacherViewSet

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'profiles', UserProfileViewSet, basename='user-profile')
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('me/', UserViewSet.as_view({'get': 'me', 'put': 'update_me'}), name='user-me'),
    path('change-password/', UserViewSet.as_view({'post': 'change_password'}), name='user-change-password'),
    path('', include(router.urls)),
]
