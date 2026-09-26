"""Har bir shablonga sayt sozlamalari, menyu yoʻnalishlari va SITE_URL."""
from django.conf import settings

from .models import Direction, SiteSettings
from .sitetext import widget_overrides


def site_settings(request):
    return {
        "site": SiteSettings.load(),
        "nav_directions": Direction.objects.all(),
        "SITE_URL": settings.SITE_URL,
        "widget_texts": widget_overrides(),
    }
