"""Второй раунд баг-скана: граничные случаи авторизации."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthEdgeCaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="edge_auth", password="StrongPass!234", email="edge_auth@example.com"
        )

    def test_open_redirect_is_ignored(self):
        response = self.client.post(
            reverse("accounts:login") + "?next=https://evil.example/phish",
            {"username": "edge_auth", "password": "StrongPass!234"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard:home"))

    def test_safe_next_is_respected(self):
        response = self.client.post(
            reverse("accounts:login") + "?next=" + reverse("accounts:profile"),
            {"username": "edge_auth", "password": "StrongPass!234"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:profile"))

    def test_inactive_user_cannot_login(self):
        User.objects.create_user(
            username="edge_off", password="StrongPass!234", is_active=False
        )
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "edge_off", "password": "StrongPass!234"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_password_mismatch_is_rejected(self):
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "edge_mismatch",
                "first_name": "A",
                "email": "mismatch@example.com",
                "password1": "StrongPass!234",
                "password2": "StrongPass!235",
            },
        )
        self.assertFalse(User.objects.filter(username="edge_mismatch").exists())

    def test_weak_password_is_rejected(self):
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "edge_weak",
                "first_name": "A",
                "email": "weak@example.com",
                "password1": "123",
                "password2": "123",
            },
        )
        self.assertFalse(User.objects.filter(username="edge_weak").exists())

    def test_duplicate_username_is_rejected(self):
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "edge_auth",
                "first_name": "A",
                "email": "dup2@example.com",
                "password1": "StrongPass!234",
                "password2": "StrongPass!234",
            },
        )
        self.assertEqual(User.objects.filter(username="edge_auth").count(), 1)
