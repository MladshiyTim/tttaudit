from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from core.media import lead_attachment, public_media, public_media_pattern
from core.sitemaps import SITEMAPS

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin-files/lead/<int:pk>/", lead_attachment, name="lead_attachment"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="core/robots.txt", content_type="text/plain")),
    # DEBUG va prodda bir xil: faqat PUBLIC_MEDIA_PREFIXES; leads/ va boshqalar 404
    re_path(public_media_pattern(), public_media, name="public_media"),
]

# Har bir til oʻz prefiksida: /uz/ /ru/ /en/
urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    prefix_default_language=True,
)
