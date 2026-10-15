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
class HomeworkFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher", password="pass12345", role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username="student", password="pass12345", email="student@example.com"
        )
        self.module = CourseModule.objects.create(order=99, title="Тестовый модуль", summary="...")
        self.assignment = Assignment.objects.create(
            module=self.module,
            title="Тестовое задание",
            description="Сделайте что-нибудь",
            max_score=100,
            order=1,
        )

    def _upload(self, name="solution.py"):
        upload = SimpleUploadedFile(name, b"print('hello')\n", content_type="text/x-python")
        return self.client.post(
            reverse("homework:assignment_detail", args=[self.assignment.pk]),
            {"file": upload, "comment": "Готово"},
        )

    def test_student_uploads_submission(self):
        self.client.force_login(self.student)
        response = self._upload()
        self.assertRedirects(response, reverse("homework:assignment_detail", args=[self.assignment.pk]))
        submission = Submission.objects.get()
        self.assertEqual(submission.student, self.student)
        self.assertEqual(submission.status, Submission.Status.SUBMITTED)

    def test_teacher_reviews_submission(self):
        self.client.force_login(self.student)
        self._upload()
        submission = Submission.objects.get()

        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("homework:submission_detail", args=[submission.pk]),
            {"review-score": 90, "review-feedback": "Отличная работа", "status": "reviewed"},
        )
        self.assertRedirects(response, reverse("homework:submission_detail", args=[submission.pk]))
        review = Review.objects.get(submission=submission)
        self.assertEqual(review.score, 90)
        self.assertEqual(review.reviewer, self.teacher)
        submission.refresh_from_db()
        self.assertEqual(submission.status, Submission.Status.REVIEWED)

    def test_score_cannot_exceed_max(self):
        self.client.force_login(self.student)
        self._upload()
        submission = Submission.objects.get()

        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("homework:submission_detail", args=[submission.pk]),
            {"review-score": 500, "review-feedback": "Много", "status": "reviewed"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.exists())

    def test_student_cannot_review(self):
        self.client.force_login(self.student)
        self._upload()
        submission = Submission.objects.get()
        response = self.client.get(reverse("homework:submission_detail", args=[submission.pk]))
        self.assertEqual(response.status_code, 403)

    def test_unpublished_assignment_hidden_from_list(self):
        Assignment.objects.create(
            title="Черновик", description="...", is_published=False, order=2
        )
        self.client.force_login(self.student)
        response = self.client.get(reverse("homework:assignment_list"))
        self.assertContains(response, "Тестовое задание")
        self.assertNotContains(response, "Черновик")

    def test_teacher_can_create_assignment(self):
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("homework:assignment_create"),
            {
                "title": "Новое ДЗ",
                "description": "Описание",
                "max_score": 50,
                "order": 3,
                "module": self.module.pk,
                "is_published": "on",
            },
        )
        self.assertRedirects(response, reverse("homework:manage_assignments"))
        self.assertTrue(Assignment.objects.filter(title="Новое ДЗ").exists())

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class MessagingTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="chat_teacher", password="pass12345", role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username="chat_student", password="pass12345", email="chat@example.com"
        )
        self.other_student = User.objects.create_user(username="chat_other", password="pass12345")
        self.assignment = Assignment.objects.create(
            title="ДЗ с обсуждением", description="...", max_score=100, order=10
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            file=SimpleUploadedFile("work.py", b"print(1)", content_type="text/x-python"),
        )

    def test_student_message_visible_to_teacher_and_marked_read(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("homework:post_message", args=[self.submission.pk]),
            {"body": "Подскажите, верно ли я понял задание?"},
        )
        self.assertRedirects(
            response, reverse("homework:assignment_detail", args=[self.assignment.pk])
        )
        message = SubmissionMessage.objects.get()
        self.assertEqual(message.author, self.student)

        self.client.force_login(self.teacher)
        response = self.client.get(
            reverse("homework:submission_detail", args=[self.submission.pk])
        )
        self.assertContains(response, "Подскажите, верно ли я понял задание?")
        message.refresh_from_db()
        self.assertTrue(message.is_read)

    def test_teacher_reply_visible_to_student(self):
        SubmissionMessage.objects.create(
            submission=self.submission, author=self.student, body="Первый вопрос"
        )
        self.client.force_login(self.teacher)
        self.client.post(
            reverse("homework:post_message", args=[self.submission.pk]),
            {"body": "Проверьте строку 3"},
        )
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("homework:assignment_detail", args=[self.assignment.pk])
        )
        self.assertContains(response, "Проверьте строку 3")

    def test_other_student_cannot_post(self):
        self.client.force_login(self.other_student)
        response = self.client.post(
            reverse("homework:post_message", args=[self.submission.pk]), {"body": "чужое"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(SubmissionMessage.objects.exists())

    def test_empty_message_is_rejected(self):
        self.client.force_login(self.student)
        self.client.post(
            reverse("homework:post_message", args=[self.submission.pk]), {"body": "   "}
        )
        self.assertFalse(SubmissionMessage.objects.exists())

    def test_student_dashboard_counts_unread_teacher_messages(self):
        SubmissionMessage.objects.create(
            submission=self.submission, author=self.teacher, body="Есть вопрос к работе"
        )
        self.client.force_login(self.student)
        response = self.client.get(reverse("dashboard:student"))
        self.assertContains(response, "Новых сообщений от преподавателя: 1")

    def test_teacher_dashboard_counts_unread_student_questions(self):
        SubmissionMessage.objects.create(
            submission=self.submission, author=self.student, body="Помогите, пожалуйста"
        )
        self.client.force_login(self.teacher)
        response = self.client.get(reverse("dashboard:teacher"))
        self.assertContains(response, "Вопросов от студентов без ответа: 1")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TeacherQueueTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="queue_teacher", password="pass12345", role=User.Role.TEACHER
        )
        self.first_student = User.objects.create_user(
            username="queue_one", password="pass12345", email="one@example.com"
        )
        self.second_student = User.objects.create_user(
            username="queue_two", password="pass12345", email="two@example.com"
        )
        self.assignment = Assignment.objects.create(
            title="Очередь проверки", description="...", max_score=100, order=20
        )
        self.first = Submission.objects.create(
            assignment=self.assignment,
            student=self.first_student,
            file=SimpleUploadedFile("one.py", b"one", content_type="text/x-python"),
        )
        self.second = Submission.objects.create(
            assignment=self.assignment,
            student=self.second_student,
            file=SimpleUploadedFile("two.py", b"two", content_type="text/x-python"),
        )

    def test_save_and_next_redirects_to_next_pending(self):
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("homework:submission_detail", args=[self.first.pk]),
            {
                "review-score": 80,
                "review-feedback": "Хорошо",
                "status": "reviewed",
                "next_submission": "1",
            },
        )
        self.assertRedirects(
            response, reverse("homework:submission_detail", args=[self.second.pk])
        )
        self.first.refresh_from_db()
        self.assertEqual(self.first.status, Submission.Status.REVIEWED)

    def test_review_page_offers_next_pending_button(self):
        self.client.force_login(self.teacher)
        response = self.client.get(
            reverse("homework:submission_detail", args=[self.first.pk])
        )
        self.assertContains(response, "Сохранить и проверить следующую")

    def test_teacher_dashboard_offers_queue_cta(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse("dashboard:teacher"))
        self.assertContains(response, "Проверить следующую")
        self.assertContains(response, "Очередь проверки")
