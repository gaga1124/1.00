from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet, NotificationAttachmentViewSet,
    NotificationSettingViewSet, NotificationLogViewSet
)

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')
router.register(r'logs', NotificationLogViewSet, basename='notification-log')

urlpatterns = [
    path('', include(router.urls)),
    path('attachments/<int:pk>/download/', NotificationAttachmentViewSet.as_view({'get': 'download'}), name='attachment-download'),
    path('attachments/<int:pk>/delete/', NotificationAttachmentViewSet.as_view({'delete': 'delete'}), name='attachment-delete'),
    path('settings/', NotificationSettingViewSet.as_view({'get': 'my_settings', 'put': 'update_settings'}), name='notification-settings'),
    path('my-logs/', NotificationLogViewSet.as_view({'get': 'my_logs'}), name='my-logs'),
    path('logs-stats/', NotificationLogViewSet.as_view({'get': 'stats'}), name='logs-stats'),
]
