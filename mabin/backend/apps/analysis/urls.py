from django.urls import path
from .views import DashboardStatsView, WarningSystemView, DecisionSupportView

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='analysis-dashboard'),
    path('warnings/', WarningSystemView.as_view(), name='analysis-warnings'),
    path('decision-support/', DecisionSupportView.as_view(), name='analysis-decision-support'),
]
