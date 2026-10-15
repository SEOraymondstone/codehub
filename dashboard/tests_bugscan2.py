"""Второй раунд баг-скана: маршрутизация кабинетов."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class DashboardRoutingEdgeTests(TestCase):
    def test_teacher_on_student_dashboard_is_redirected(self):
        teacher = User.objects.create_user(
            username="route_teacher", password="pass12345", role=User.Role.TEACHER
        )
        self.client.force_login(teacher)
        response = self.client.get(reverse("dashboard:student"))
        self.assertRedirects(response, reverse("dashboard:teacher"))

    def test_superuser_is_routed_to_teacher_cabinet(self):
        root = User.objects.create_superuser(
            username="route_root", email="root@example.com", password="pass12345"
        )
        self.client.force_login(root)
        response = self.client.get(reverse("dashboard:home"))
        self.assertRedirects(response, reverse("dashboard:teacher"))

    def test_teacher_assignment_list_redirects_to_manage(self):
        teacher = User.objects.create_user(
            username="route_teacher2", password="pass12345", role=User.Role.TEACHER
        )
        self.client.force_login(teacher)
        response = self.client.get(reverse("homework:assignment_list"))
        self.assertRedirects(response, reverse("homework:manage_assignments"))
