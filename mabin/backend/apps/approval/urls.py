from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LeaveApplicationViewSet, ReimbursementApplicationViewSet,
    PartyMembershipApplicationViewSet
)

router = DefaultRouter()
router.register(r'leave', LeaveApplicationViewSet, basename='leave-application')
router.register(r'reimbursement', ReimbursementApplicationViewSet, basename='reimbursement-application')
router.register(r'party', PartyMembershipApplicationViewSet, basename='party-application')

urlpatterns = [
    path('', include(router.urls)),
]
