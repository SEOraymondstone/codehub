from django.test import TestCase
from django.urls import reverse

from .models import CourseModule, Lead


class LandingPageTests(TestCase):
    def setUp(self):
        CourseModule.objects.create(
            order=1, title="Модуль 1", summary="Описание", topics="Тема 1\nТема 2"
        )

    def test_landing_renders_program_and_price(self):
        response = self.client.get(reverse("pages:landing"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CodeHub")
        self.assertContains(response, "Модуль 1")
        self.assertContains(response, "$100")

    def test_landing_uses_soft_public_theme(self):
        response = self.client.get(reverse("pages:landing"))
        self.assertContains(response, "css/public.css")
        self.assertNotContains(response, "css/style.css")

    def test_lead_form_creates_lead(self):
        response = self.client.post(
            reverse("pages:landing"),
            {
                "lead_submit": "1",
                "source": "hero",
                "lead-name": "Пётр",
                "lead-phone": "+79991234567",
                "lead-email": "petr@example.com",
                "lead-message": "Хочу на курс",
            },
        )
        self.assertRedirects(response, reverse("pages:landing"))
        lead = Lead.objects.get()
        self.assertEqual(lead.name, "Пётр")
        self.assertEqual(lead.source, Lead.Source.HERO)

    def test_honeypot_blocks_spam(self):
        self.client.post(
            reverse("pages:landing"),
            {
                "lead_submit": "1",
                "lead-name": "Бот",
                "lead-phone": "+70000000000",
                "lead-website": "http://spam.example",
            },
        )
        self.assertEqual(Lead.objects.count(), 0)

    def test_contact_form_creates_message(self):
        response = self.client.post(
            reverse("pages:landing"),
            {
                "contact_submit": "1",
                "contact-name": "Анна",
                "contact-email": "anna@example.com",
                "contact-subject": "Вопрос",
                "contact-message": "Когда старт?",
            },
        )
        self.assertRedirects(response, reverse("pages:landing"))
        self.assertEqual(self.client.get(reverse("pages:landing")).status_code, 200)
