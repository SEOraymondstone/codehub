"""Дополнительные проверки на баги (edge cases)."""

import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from courses.models import CourseModule

from .models import Assignment, Review, Submission, SubmissionMessage

User = get_user_model()
MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class EdgeCaseTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="edge_teacher", password="pass12345", role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username="edge_student", password="pass12345", email="edge@example.com"
        )
        self.other = User.objects.create_user(username="edge_other", password="pass12345")
        self.module = CourseModule.objects.first()
        self.assignment = Assignment.objects.create(
            module=self.module, title="Edge ДЗ", description="...", max_score=100, order=90
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            file=SimpleUploadedFile("edge.py", b"print(1)", content_type="text/x-python"),
        )

    # --- 1. «Сохранить и проверить следующую» должно закрывать вопрос студента ---
    def test_save_and_next_marks_student_question_as_read(self):
        SubmissionMessage.objects.create(
            submission=self.submission, author=self.student, body="Вопрос по работе"
        )
        second_assignment = Assignment.objects.create(
            module=self.module, title="Edge ДЗ 2", description="...", max_score=100, order=91
        )
        Submission.objects.create(
            assignment=second_assignment,
            student=self.other,
            file=SimpleUploadedFile("edge2.py", b"print(2)", content_type="text/x-python"),
        )

        self.client.force_login(self.teacher)
        self.client.post(
            reverse("homework:submission_detail", args=[self.submission.pk]),
            {
                "review-score": 90,
                "review-feedback": "Хорошо",
                "status": "reviewed",
                "next_submission": "1",
            },
        )
        message = SubmissionMessage.objects.get()
        self.assertTrue(message.is_read, "вопрос должен считаться прочитанным после проверки")

    # --- 2. Не-админ не должен видеть ссылку в /admin/ ---
    def test_non_staff_teacher_does_not_see_admin_link(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse("dashboard:teacher"))
        self.assertNotContains(response, "/admin/courses/lead/")

    # --- 3. Пустой комментарий к работе не ломает повторную отправку ---
    def test_resubmit_without_new_file_keeps_working(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("homework:assignment_detail", args=[self.assignment.pk]),
            {"comment": "только комментарий"},
        )
        self.assertRedirects(
            response, reverse("homework:assignment_detail", args=[self.assignment.pk])
        )

    # --- 4. Некорректный файл отклоняется ---
    def test_disallowed_extension_is_rejected(self):
        self.client.force_login(self.student)
        bad = SimpleUploadedFile("virus.exe", b"MZ", content_type="application/octet-stream")
        response = self.client.post(
            reverse("homework:assignment_detail", args=[self.assignment.pk]),
            {"file": bad, "comment": "плохой файл"},
        )
        self.assertEqual(response.status_code, 200)
        self.submission.refresh_from_db()
        self.assertNotIn("virus.exe", self.submission.file.name)

    # --- 5. Студент не может писать сообщение к чужой работе ---
    def test_other_student_cannot_read_thread(self):
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("homework:post_message", args=[self.submission.pk]), {"body": "чужое"}
        )
        self.assertEqual(response.status_code, 403)

    # --- 6. Проверка работы без балла не проходит ---
    def test_review_requires_score(self):
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("homework:submission_detail", args=[self.submission.pk]),
            {"review-score": "", "review-feedback": "текст", "status": "reviewed"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.filter(submission=self.submission).exists())

    # --- 7. Заявка без телефона не создаётся ---
    def test_lead_requires_phone(self):
        from courses.models import Lead

        response = self.client.post(
            reverse("pages:landing"),
            {"lead_submit": "1", "lead-name": "Иван", "lead-phone": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Lead.objects.exists())

    # --- 8. Неопубликованное задание недоступно студенту ---
    def test_unpublished_assignment_is_blocked(self):
        draft = Assignment.objects.create(
            title="Черновик", description="...", is_published=False, order=92
        )
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("homework:assignment_detail", args=[draft.pk])
        )
        self.assertRedirects(response, reverse("homework:assignment_list"))

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SecurityAndRobustnessTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="sec_teacher", password="pass12345", role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username="sec_student", password="pass12345", email="sec@example.com"
        )
        self.assignment = Assignment.objects.create(
            title="Security ДЗ", description="...", max_score=100, order=95
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            file=SimpleUploadedFile("sec.py", b"print(1)", content_type="text/x-python"),
        )

    def test_student_cannot_open_teacher_endpoints(self):
        self.client.force_login(self.student)
        for url in (
            reverse("homework:submission_list"),
            reverse("homework:submission_detail", args=[self.submission.pk]),
            reverse("homework:manage_assignments"),
            reverse("homework:assignment_create"),
            reverse("homework:assignment_edit", args=[self.assignment.pk]),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_anonymous_redirected_to_login(self):
        for url in (
            reverse("homework:assignment_detail", args=[self.assignment.pk]),
            reverse("homework:post_message", args=[self.submission.pk]),
            reverse("dashboard:student"),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("accounts:login"), response.url)

    def test_get_on_post_message_does_not_create(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("homework:post_message", args=[self.submission.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SubmissionMessage.objects.exists())

    def test_message_html_is_escaped(self):
        self.client.force_login(self.student)
        self.client.post(
            reverse("homework:post_message", args=[self.submission.pk]),
            {"body": "<script>alert(1)</script>"},
        )
        self.client.force_login(self.teacher)
        response = self.client.get(
            reverse("homework:submission_detail", args=[self.submission.pk])
        )
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_missing_objects_return_404(self):
        self.client.force_login(self.teacher)
        self.assertEqual(
            self.client.get(reverse("homework:submission_detail", args=[99999])).status_code, 404
        )
        self.client.force_login(self.student)
        self.assertEqual(
            self.client.get(reverse("homework:assignment_detail", args=[99999])).status_code, 404
        )

    def test_logout_requires_post(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)

    def test_invalid_review_status_falls_back_to_reviewed(self):
        self.client.force_login(self.teacher)
        self.client.post(
            reverse("homework:submission_detail", args=[self.submission.pk]),
            {"review-score": 50, "review-feedback": "ок", "status": "hacked; DROP TABLE"},
        )
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, Submission.Status.REVIEWED)

    def test_needs_revision_sets_student_focus(self):
        self.client.force_login(self.teacher)
        self.client.post(
            reverse("homework:submission_detail", args=[self.submission.pk]),
            {"review-score": 40, "review-feedback": "Доработайте", "status": "needs_revision"},
        )
        self.client.force_login(self.student)
        response = self.client.get(reverse("dashboard:student"))
        self.assertContains(response, "на доработке")

    def test_second_upload_updates_same_submission(self):
        self.client.force_login(self.student)
        new_file = SimpleUploadedFile("sec2.py", b"print(2)", content_type="text/x-python")
        self.client.post(
            reverse("homework:assignment_detail", args=[self.assignment.pk]),
            {"file": new_file, "comment": "версия 2"},
        )
        self.assertEqual(Submission.objects.filter(student=self.student).count(), 1)

    def test_healthz(self):
        response = self.client.get(reverse("pages:healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
