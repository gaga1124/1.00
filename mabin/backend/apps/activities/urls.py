from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SocialPracticeViewSet, CompetitionViewSet, CompetitionTeamViewSet,
    DynamicActivityTypeViewSet, DynamicActivityInstanceViewSet
)

router = DefaultRouter()
router.register(r'social-practices', SocialPracticeViewSet)
router.register(r'competitions', CompetitionViewSet)
router.register(r'competition-teams', CompetitionTeamViewSet)
router.register(r'dynamic-types', DynamicActivityTypeViewSet)
router.register(r'dynamic-instances', DynamicActivityInstanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
