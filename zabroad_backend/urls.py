from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/",         admin.site.urls),
    path("api/auth/",      include("accounts.urls")),
    path("api/posts/",     include("posts.urls")),
    path("api/jobs/",      include("jobs.urls")),
    path("api/housing/",   include("housing.urls")),
    path("api/doctors/",   include("healthcare.urls")),
    path("api/attorneys/", include("attorneys.urls")),
    path("api/events/",    include("events.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
