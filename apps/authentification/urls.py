"""
Sigma-ALS URL Configuration
Multi-sector API routing for Mathematics, Agriculture, and TVET education
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# API versioning and documentation
api_v1_patterns = [
    # Authentication endpoints
    path('auth/', include('apps.authentication.urls')),
    
    # Multi-sector educational content
    path('', include('apps.multi_sector.urls')),
    
    # AI engine and content generation
    path('ai/', include('apps.ai_engine.urls')),
    
    # Teacher oversight and quality control
    path('teacher/', include('apps.teacher_oversight.urls')),
    
    # Offline synchronization
    path('sync/', include('apps.offline_sync.urls')),
]

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/', include(api_v1_patterns)),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar for development
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Custom error handlers for production
if not settings.DEBUG:
    from django.views.generic import TemplateView
    
    handler404 = TemplateView.as_view(template_name='404.html')
    handler500 = TemplateView.as_view(template_name='500.html')
