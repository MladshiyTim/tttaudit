"""Sitemap: statik sahifalar, yoʻnalishlar, xizmatlar, maqolalar — uch tilda alternates bilan."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Direction, Post, Service


class StaticSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ["core:home", "core:services", "core:registry", "core:credentials", "core:legislation",
                "core:news", "core:company", "core:team", "core:instruments", "core:requisites",
                "core:contact", "core:request"]

    def location(self, item):
        return reverse(item)


class DirectionSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    priority = 0.9

    def items(self):
        return Direction.objects.all()


class ServiceSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    priority = 0.9

    def items(self):
        return Service.objects.select_related("direction")


class PostSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    changefreq = "weekly"

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_on


SITEMAPS = {"static": StaticSitemap, "directions": DirectionSitemap, "services": ServiceSitemap, "posts": PostSitemap}
