from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_healthz_returns_ok(self):
        response = self.client.get(reverse("pages:healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_landing_is_public(self):
        response = self.client.get(reverse("pages:landing"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CodeHub")


class GuidePageTests(TestCase):
    def test_guide_page_is_dark_and_public(self):
        response = self.client.get(reverse("pages:guide"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "public-dark.css")
        self.assertContains(response, "theme-public--dark")
        self.assertContains(response, "Как учиться")

    def test_landing_links_to_guide(self):
        response = self.client.get(reverse("pages:landing"))
        self.assertContains(response, reverse("pages:guide"))

    def test_guide_shows_human_readable_upload_limit(self):
        response = self.client.get(reverse("pages:guide"))
        self.assertContains(response, "1 ГБ")


class UploadLimitTests(TestCase):
    def test_limit_is_at_least_one_gigabyte(self):
        self.assertGreaterEqual(settings.HOMEWORK_MAX_UPLOAD_SIZE, 1024**3)

class EditableContentTests(TestCase):
    """Контент сайта редактируется через админку и сразу виден на лендинге."""

    def test_site_settings_override_defaults(self):
        from .models import SiteSettings

        site = SiteSettings.load()
        site.name = "CodeHub Academy"
        site.save()

        response = self.client.get(reverse("pages:landing"))
        self.assertContains(response, "CodeHub Academy")

    def test_seeded_content_blocks_render(self):
        response = self.client.get(reverse("pages:landing"))
        for marker in (
            "stat__value",
            "pricing-card__price",
            "testimonial__author",
            "teacher-card",
            "code-window__bar",
            "marquee__track",
        ):
            with self.subTest(marker=marker):
                self.assertContains(response, marker)

    def test_unpublished_block_is_hidden(self):
        from .models import Advantage

        Advantage.objects.update(is_published=False)
        response = self.client.get(reverse("pages:landing"))
        self.assertNotContains(response, 'id="advantages"')

    def test_site_settings_singleton(self):
        from .models import SiteSettings

        other = SiteSettings(name="Второй")
        other.save()  # синглтон всегда пишется в pk=1
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.load().name, "Второй")

class SeoAndTrustTests(TestCase):
    def test_robots_txt(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sitemap:", response.content.decode())

    def test_sitemap_lists_public_pages(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("/guide/", body)
        self.assertIn("/privacy/", body)

    def test_privacy_page_is_public(self):
        response = self.client.get(reverse("pages:privacy"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Политика конфиденциальности")

    def test_landing_has_seo_meta_and_jsonld(self):
        response = self.client.get(reverse("pages:landing"))
        self.assertContains(response, 'rel="canonical"')
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, "application/ld+json")

    def test_footer_links_to_privacy(self):
        response = self.client.get(reverse("pages:landing"))
        self.assertContains(response, reverse("pages:privacy"))
