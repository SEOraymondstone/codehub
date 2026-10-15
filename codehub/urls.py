"""CodeHub URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponseForbidden
from django.urls import include, path, re_path

from pages import views as pages_views
from pages.sitemaps import StaticViewSitemap

sitemaps = {"static": StaticViewSitemap}

admin.site.site_header = "CodeHub — панель управления"
admin.site.site_title = "CodeHub"
admin.site.index_title = "Управление курсом"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", pages_views.robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("homework/", include("homework.urls")),
    path("", include("pages.urls")),
]

def private_media_blocked(request, *args, **kwargs):
    """Прямой доступ к файлам домашних работ закрыт — только через кабинет."""
    return HttpResponseForbidden("Файлы работ доступны только из личного кабинета.")


if settings.DEBUG:
    # Важно: этот шаблон идёт раньше раздачи MEDIA.
    urlpatterns += [re_path(r"^media/submissions/", private_media_blocked)]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
