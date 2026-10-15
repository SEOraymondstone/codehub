from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Single user model for students and teachers/admins."""

    class Role(models.TextChoices):
        STUDENT = "student", "Студент"
        TEACHER = "teacher", "Преподаватель"
        ADMIN = "admin", "Администратор"

    role = models.CharField(
        "Роль", max_length=20, choices=Role.choices, default=Role.STUDENT, db_index=True
    )
    phone = models.CharField("Телефон", max_length=32, blank=True)
    telegram = models.CharField("Telegram", max_length=64, blank=True)
    bio = models.TextField("О себе", blank=True)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("-date_joined",)

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def get_absolute_url(self) -> str:
        return reverse("dashboard:home")

    # -- Role helpers ------------------------------------------------------
    @property
    def is_student(self) -> bool:
        return self.role == self.Role.STUDENT and not self.is_superuser

    @property
    def is_teacher(self) -> bool:
        return self.role in {self.Role.TEACHER, self.Role.ADMIN} or self.is_superuser

    @property
    def display_name(self) -> str:
        return self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        # Superusers always keep full teacher-level access.
        if self.is_superuser:
            self.role = self.Role.ADMIN
            self.is_staff = True
        super().save(*args, **kwargs)


class StudentProfile(models.Model):
    """Extra enrolment data attached to a student account."""

    class Level(models.TextChoices):
        BEGINNER = "beginner", "С нуля"
        BASIC = "basic", "Есть базовые знания"
        ADVANCED = "advanced", "Продолжающий"

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="Пользователь"
    )
    level = models.CharField(
        "Уровень подготовки", max_length=20, choices=Level.choices, default=Level.BEGINNER
    )
    goal = models.CharField("Цель обучения", max_length=200, blank=True)
    enrolled_at = models.DateField("Дата зачисления", null=True, blank=True)

    class Meta:
        verbose_name = "Профиль студента"
        verbose_name_plural = "Профили студентов"

    def __str__(self) -> str:
        return f"Профиль: {self.user.display_name}"
