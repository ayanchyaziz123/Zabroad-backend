from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path("admin/",         admin.site.urls),
    path("api/auth/",      include("accounts.urls")),
    path("api/posts/",     include("posts.urls")),
    path("api/jobs/",      include("jobs.urls")),
    path("api/housing/",   include("housing.urls")),
    path("api/doctors/",   include("healthcare.urls")),
    path("api/attorneys/", include("attorneys.urls")),
    path("api/events/",    include("events.urls")),
    path("api/chat/",          include("chat.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/marketplace/",   include("marketplace.urls")),
    path("api/ai/",            include("ai.urls")),
]

# Serve media files in both DEBUG and production.
# Django's static() helper only works when DEBUG=True; this pattern always works.
# When USE_S3=True the MEDIA_ROOT is empty so this is a no-op.
if not getattr(settings, 'DEFAULT_FILE_STORAGE', '').endswith('S3Boto3Storage'):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
