from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AwardTypeViewSet, AwardApplicationViewSet, AwardPublicityViewSet

router = DefaultRouter()
router.register(r'types', AwardTypeViewSet, basename='award-type')
router.register(r'applications', AwardApplicationViewSet, basename='award-application')
router.register(r'publicities', AwardPublicityViewSet, basename='award-publicity')

urlpatterns = [
    path('', include(router.urls)),
]
