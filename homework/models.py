from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from codehub.utils import max_upload_label
from courses.models import CourseModule

ALLOWED_UPLOAD_EXTENSIONS = [
    "zip", "rar", "7z", "tar", "gz",
    "py", "js", "ts", "java", "kt", "cs", "go", "rb", "php", "c", "cpp", "h",
    "html", "css", "scss", "sql", "json", "txt", "md", "pdf", "doc", "docx",
    "ipynb", "png", "jpg", "jpeg",
]


class Assignment(models.Model):
    """A homework task created by the teacher for a course module."""

    module = models.ForeignKey(
        CourseModule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
        verbose_name="Модуль",
    )
    title = models.CharField("Название задания", max_length=200)
    description = models.TextField("Описание задания")
    max_score = models.PositiveIntegerField("Максимальный балл", default=100)
    deadline = models.DateTimeField("Дедлайн", null=True, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)
    is_published = models.BooleanField("Опубликовано", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"
        ordering = ("order", "id")

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("homework:assignment_detail", args=[self.pk])

    @property
    def is_overdue(self) -> bool:
        return bool(self.deadline and self.deadline < timezone.now())

    def submissions_count(self) -> int:
        return self.submissions.count()


class Submission(models.Model):
    """A student's uploaded solution for an assignment."""

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "На проверке"
        IN_REVIEW = "in_review", "Проверяется"
        REVIEWED = "reviewed", "Проверено"
        NEEDS_REVISION = "needs_revision", "На доработку"

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions", verbose_name="Задание"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Студент",
    )
    file = models.FileField(
        "Файл работы",
        upload_to="submissions/%Y/%m/",
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_UPLOAD_EXTENSIONS)],
    )
    comment = models.TextField("Комментарий студента", blank=True)
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.SUBMITTED, db_index=True
    )
    submitted_at = models.DateTimeField("Отправлено", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Работа студента"
        verbose_name_plural = "Работы студентов"
        ordering = ("-updated_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("assignment", "student"), name="unique_submission_per_student"
            )
        ]

    def __str__(self) -> str:
        return f"{self.assignment} — {self.student.display_name}"

    def get_absolute_url(self) -> str:
        return reverse("homework:submission_detail", args=[self.pk])

    @property
    def is_reviewed(self) -> bool:
        return hasattr(self, "review")

    @property
    def score(self):
        review = getattr(self, "review", None)
        return review.score if review else None

    def unread_from_teacher(self) -> int:
        return self.messages.filter(is_read=False).exclude(author_id=self.student_id).count()

    def unread_from_student(self) -> int:
        return self.messages.filter(is_read=False, author_id=self.student_id).count()

    def clean(self):
        super().clean()
        if self.file and getattr(self.file, "size", 0) > settings.HOMEWORK_MAX_UPLOAD_SIZE:
            from django.core.exceptions import ValidationError

            raise ValidationError({"file": f"Файл больше допустимых {max_upload_label()}."})


class Review(models.Model):
    """Teacher's grade and feedback for a submission."""

    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE, related_name="review", verbose_name="Работа"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reviews",
        verbose_name="Проверяющий",
    )
    score = models.PositiveIntegerField("Балл", default=0)
    feedback = models.TextField("Обратная связь")
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Проверка работы"
        verbose_name_plural = "Проверки работ"
        ordering = ("-updated_at",)

    def __str__(self) -> str:
        return f"Проверка: {self.submission} — {self.score}"

    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()
        if self.submission_id and self.score > self.submission.assignment.max_score:
            raise ValidationError(
                {"score": f"Балл не может превышать {self.submission.assignment.max_score}."}
            )


class SubmissionMessage(models.Model):
    """Сообщение в переписке студента и преподавателя по конкретной работе."""

    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Работа",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="submission_messages",
        verbose_name="Автор",
    )
    body = models.TextField("Сообщение")
    is_read = models.BooleanField("Прочитано", default=False, db_index=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Сообщение по работе"
        verbose_name_plural = "Сообщения по работам"
        ordering = ("created_at", "id")

    def __str__(self) -> str:
        return f"{self.author} -> {self.submission_id}: {self.body[:40]}"

    @property
    def is_from_teacher(self) -> bool:
        return bool(self.author and self.author.is_teacher)

