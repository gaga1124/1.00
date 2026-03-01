from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartyBranchViewSet, PartyMemberViewSet, PartyActivityViewSet

router = DefaultRouter()
router.register(r'branches', PartyBranchViewSet)
router.register(r'members', PartyMemberViewSet)
router.register(r'activities', PartyActivityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
