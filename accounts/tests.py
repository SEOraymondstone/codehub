from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserModelTests(TestCase):
    def test_default_role_is_student(self):
        user = User.objects.create_user(username="s1", password="pass12345")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_teacher)

    def test_teacher_role_helpers(self):
        teacher = User.objects.create_user(
            username="t1", password="pass12345", role=User.Role.TEACHER
        )
        self.assertTrue(teacher.is_teacher)
        self.assertFalse(teacher.is_student)

    def test_superuser_gets_admin_role(self):
        root = User.objects.create_superuser(
            username="root", email="root@example.com", password="pass12345"
        )
        self.assertEqual(root.role, User.Role.ADMIN)
        self.assertTrue(root.is_teacher)


class RegistrationTests(TestCase):
    def test_registration_creates_student_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newbie",
                "first_name": "Иван",
                "last_name": "Тестов",
                "email": "newbie@example.com",
                "phone": "+79990000000",
                "password1": "StrongPass!234",
                "password2": "StrongPass!234",
            },
        )
        self.assertRedirects(
            response, reverse("dashboard:home"), fetch_redirect_response=False
        )
        user = User.objects.get(username="newbie")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.profile)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(username="a", password="pass12345", email="dup@example.com")
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "b",
                "first_name": "B",
                "email": "dup@example.com",
                "password1": "StrongPass!234",
                "password2": "StrongPass!234",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже зарегистрирован")


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student", password="StrongPass!234")

    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вход в кабинет")

    def test_cabinet_uses_terminal_theme(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, "css/style.css")
        self.assertNotContains(response, "css/public.css")

    def test_branding_is_not_shadowed_by_request_site(self):
        # Django auth views inject a RequestSite into the "site" context key;
        # branding must keep rendering the configured project name.
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, "CodeHub")
        self.assertNotContains(response, "testserver")

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("accounts:login"), {"username": "student", "password": "StrongPass!234"}
        )
        self.assertRedirects(
            response, reverse("dashboard:home"), fetch_redirect_response=False
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)


class PermissionTests(TestCase):
    def test_student_cannot_open_teacher_cabinet(self):
        student = User.objects.create_user(username="s", password="pass12345")
        self.client.force_login(student)
        response = self.client.get(reverse("dashboard:teacher"))
        self.assertEqual(response.status_code, 403)

class ProfileFormTests(TestCase):
    """Страница профиля содержит две формы; сохранение одной не должно затирать другую."""

    def setUp(self):
        from .models import StudentProfile

        self.user = User.objects.create_user(
            username="prof_user",
            password="pass12345",
            first_name="Иван",
            last_name="Иванов",
            email="ivan@example.com",
            phone="+79990000000",
        )
        StudentProfile.objects.create(user=self.user, level="basic", goal="хочу в IT")
        self.client.force_login(self.user)

    def test_saving_study_form_keeps_account_data(self):
        self.client.post(
            reverse("accounts:profile"),
            {"level": "advanced", "goal": "новая цель", "enrolled_at": "", "save_study": "1"},
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Иван")
        self.assertEqual(self.user.last_name, "Иванов")
        self.assertEqual(self.user.email, "ivan@example.com")
        self.assertEqual(self.user.phone, "+79990000000")
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.level, "advanced")
        self.assertEqual(self.user.profile.goal, "новая цель")

    def test_saving_account_form_keeps_study_data(self):
        self.client.post(
            reverse("accounts:profile"),
            {
                "first_name": "Пётр",
                "last_name": "Петров",
                "email": "petr@example.com",
                "phone": "+79991111111",
                "telegram": "",
                "bio": "",
                "save_account": "1",
            },
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Пётр")
        self.assertEqual(self.user.email, "petr@example.com")
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.level, "basic")
        self.assertEqual(self.user.profile.goal, "хочу в IT")
