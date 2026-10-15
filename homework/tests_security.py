"""Второй раунд баг-скана: домашние задания, лимиты и устойчивость."""

import shutil
import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from courses.models import CourseModule, Lead
from pages.models import ContactMessage

from .models import Assignment, Review, Submission, SubmissionMessage

User = get_user_model()
MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class HomeworkEdgeCaseTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="edge2_teacher", password="pass12345", role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username="edge2_student", password="pass12345", email="edge2@example.com"
        )
        self.assignment = Assignment.objects.create(
            title="Edge2 ДЗ", description="...", max_score=100, order=80
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            file=SimpleUploadedFile("edge2.py", b"print(1)", content_type="text/x-python"),
        )

    # --- отзыв обновляется, а не дублируется ---
    def test_second_review_updates_same_record(self):
        self.client.force_login(self.teacher)
        for score in (50, 80):
            self.client.post(
                reverse("homework:submission_detail", args=[self.submission.pk]),
                {"review-score": score, "review-feedback": "ок", "status": "reviewed"},
            )
        self.assertEqual(Review.objects.filter(submission=self.submission).count(), 1)
        self.assertEqual(Review.objects.get(submission=self.submission).score, 80)

    # --- просроченный дедлайн виден студенту ---
    def test_past_deadline_marks_overdue(self):
        self.assignment.deadline = timezone.now() - timedelta(days=1)
        self.assignment.save(update_fields=["deadline"])
        self.client.force_login(self.student)
        response = self.client.get(reverse("dashboard:student"))
        self.assertContains(response, "просрочено")

    # --- расширения файлов ---
    def test_uppercase_extension_is_allowed(self):
        self.client.force_login(self.student)
        upload = SimpleUploadedFile("Solution.PY", b"print(1)", content_type="text/x-python")
        response = self.client.post(
            reverse("homework:assignment_detail", args=[self.assignment.pk]),
            {"file": upload, "comment": "caps"},
        )
        self.assertRedirects(
            response, reverse("homework:assignment_detail", args=[self.assignment.pk])
        )

    def test_file_without_extension_is_rejected(self):
        self.client.force_login(self.student)
        upload = SimpleUploadedFile("solution", b"x")
        response = self.client.post(
            reverse("homework:assignment_detail", args=[self.assignment.pk]),
            {"file": upload},
        )
        self.assertEqual(response.status_code, 200)

    # --- устойчивость фильтров ---
    def test_invalid_filters_do_not_break(self):
        self.client.force_login(self.teacher)
        for query in ("status=../etc", "assignment=abc", "q=%27%20OR%201%3D1--"):
            with self.subTest(query=query):
                response = self.client.get(reverse("dashboard:teacher") + "?" + query)
                self.assertEqual(response.status_code, 200)

    # --- seed идемпотентен ---
    def test_seed_command_is_idempotent(self):
        call_command("seed_codehub")
        first = Assignment.objects.count()
        call_command("seed_codehub")
        self.assertEqual(Assignment.objects.count(), first)

    # --- CSRF ---
    def test_post_message_without_csrf_is_rejected(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.student)
        response = csrf_client.post(
            reverse("homework:post_message", args=[self.submission.pk]), {"body": "x"}
        )
        self.assertEqual(response.status_code, 403)

    # --- лимиты ввода ---
    def test_too_long_message_is_rejected(self):
        self.client.force_login(self.student)
        self.client.post(
            reverse("homework:post_message", args=[self.submission.pk]),
            {"body": "x" * 5001},
        )
        self.assertFalse(SubmissionMessage.objects.exists())

    def test_too_long_comment_is_rejected(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("homework:assignment_detail", args=[self.assignment.pk]),
            {"comment": "x" * 2001},
        )
        self.assertEqual(response.status_code, 200)

    # --- заявки и контакты ---
    def test_lead_utm_truncated_and_source_sanitised(self):
        self.client.post(
            reverse("pages:landing")
            + "?utm_source="
            + "u" * 300
            + "&utm_campaign=c",
            {
                "lead_submit": "1",
                "source": "hacker",
                "lead-name": "Тест",
                "lead-phone": "+79990000000",
            },
        )
        lead = Lead.objects.get()
        self.assertEqual(len(lead.utm_source), 120)
        self.assertEqual(lead.source, Lead.Source.OTHER)

    def test_too_long_contact_message_is_rejected(self):
        self.client.post(
            reverse("pages:landing"),
            {
                "contact_submit": "1",
                "contact-name": "Анна",
                "contact-email": "anna@example.com",
                "contact-message": "x" * 2001,
            },
        )
        self.assertFalse(ContactMessage.objects.exists())

    # --- пустой курс ---
    def test_student_dashboard_without_assignments(self):
        Assignment.objects.all().delete()
        student = User.objects.create_user(username="edge2_empty", password="pass12345")
        self.client.force_login(student)
        response = self.client.get(reverse("dashboard:student"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Задания появятся здесь")

    def test_landing_without_modules(self):
        CourseModule.objects.all().delete()
        response = self.client.get(reverse("pages:landing"))
        self.assertEqual(response.status_code, 200)

    # --- админка недоступна обычному преподавателю ---
    def test_non_staff_teacher_cannot_open_admin(self):
        self.client.force_login(self.teacher)
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class DownloadProtectionTests(TestCase):
    """Файлы работ не должны быть доступны по прямой ссылке или чужим людям."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="dl_teacher", password="pass12345", role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(username="dl_student", password="pass12345")
        self.other = User.objects.create_user(username="dl_other", password="pass12345")
        self.assignment = Assignment.objects.create(
            title="Download ДЗ", description="...", max_score=100, order=70
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            file=SimpleUploadedFile("secret.py", b"print(42)", content_type="text/x-python"),
        )

    def test_owner_can_download_file(self):
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("homework:download_submission", args=[self.submission.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])

    def test_teacher_can_download_file(self):
        self.client.force_login(self.teacher)
        response = self.client.get(
            reverse("homework:download_submission", args=[self.submission.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_other_student_cannot_download_file(self):
        self.client.force_login(self.other)
        response = self.client.get(
            reverse("homework:download_submission", args=[self.submission.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_download_file(self):
        response = self.client.get(
            reverse("homework:download_submission", args=[self.submission.pk])
        )
        self.assertEqual(response.status_code, 302)

    def test_pages_link_to_protected_download(self):
        # Тестовый раннер принудительно ставит DEBUG=False, поэтому проверяем,
        # что шаблоны ссылаются на защищённый view, а не на прямой /media/-URL.
        protected = reverse("homework:download_submission", args=[self.submission.pk])

        self.client.force_login(self.student)
        student_html = self.client.get(
            reverse("homework:assignment_detail", args=[self.assignment.pk])
        ).content.decode()
        self.assertIn(protected, student_html)
        self.assertNotIn("/media/submissions/", student_html)

        self.client.force_login(self.teacher)
        teacher_html = self.client.get(
            reverse("homework:submission_detail", args=[self.submission.pk])
        ).content.decode()
        self.assertIn(protected, teacher_html)
        self.assertNotIn("/media/submissions/", teacher_html)
