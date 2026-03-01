from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ResearchProjectViewSet, ResearchAchievementViewSet,
    ResearchTeamViewSet, TeamTaskViewSet, TeamMeetingViewSet
)

router = DefaultRouter()
router.register(r'projects', ResearchProjectViewSet)
router.register(r'achievements', ResearchAchievementViewSet)
router.register(r'teams', ResearchTeamViewSet)
router.register(r'tasks', TeamTaskViewSet)
router.register(r'meetings', TeamMeetingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
