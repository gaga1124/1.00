"""
URL configuration for college_oa project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.shortcuts import redirect

schema_view = get_schema_view(
    openapi.Info(
        title="学院OA系统 API",
        default_version='v1',
        description="学院综合办公自动化系统API文档",
        contact=openapi.Contact(email="admin@college.edu"),
    ),
    public=True,
)

urlpatterns = [
    path('', lambda request: redirect('/api/docs/')),
    path('admin/', admin.site.urls),
    
    # API文档
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # JWT认证
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 应用路由
    path('api/users/', include('apps.users.urls')),
    path('api/rbac/', include('apps.rbac.urls')),
    path('api/students/', include('apps.students.urls')),
    path('api/workflow/', include('apps.workflow.urls')),
    path('api/resources/', include('apps.resources.urls')),
    path('api/approval/', include('apps.approval.urls')),
    path('api/repair/', include('apps.repair.urls')),
    path('api/academic/', include('apps.academic.urls')),
    path('api/awards/', include('apps.awards.urls')),
    path('api/career/', include('apps.career.urls')),
    path('api/research/', include('apps.research.urls')),
    path('api/party/', include('apps.party.urls')),
    path('api/activities/', include('apps.activities.urls')),
    path('api/analysis/', include('apps.analysis.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/electronic-signature/', include('apps.electronic_signature.urls')),
    path('api/utils/', include('apps.utils.urls')),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
