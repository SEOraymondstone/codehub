from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class DashboardRoutingTests(TestCase):
    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_student_is_routed_to_student_cabinet(self):
        student = User.objects.create_user(username="s", password="pass12345")
        self.client.force_login(student)
        response = self.client.get(reverse("dashboard:home"))
        self.assertRedirects(response, reverse("dashboard:student"))

    def test_teacher_is_routed_to_teacher_cabinet(self):
        teacher = User.objects.create_user(
            username="t", password="pass12345", role=User.Role.TEACHER
        )
        self.client.force_login(teacher)
        response = self.client.get(reverse("dashboard:home"))
        self.assertRedirects(response, reverse("dashboard:teacher"))
