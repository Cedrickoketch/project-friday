from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/assistant/", include("apps.assistant.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
    path("api/calendar/", include("apps.calendar.urls")),
    path("api/news/", include("apps.news.urls")),
    path("api/subscriptions/", include("apps.subscriptions.urls")),
    # allauth
    path("accounts/", include("allauth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
