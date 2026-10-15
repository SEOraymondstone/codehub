from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Публичные страницы для sitemap.xml."""

    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return ["pages:landing", "pages:guide", "pages:privacy", "accounts:register"]

    def location(self, item):
        return reverse(item)
