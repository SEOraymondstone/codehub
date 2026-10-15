from django.db import models


class CourseModule(models.Model):
    """A module of the course programme shown on the landing page."""

    title = models.CharField("Название модуля", max_length=200)
    summary = models.TextField("Краткое описание")
    topics = models.TextField(
        "Темы (по одной в строке)", blank=True, help_text="Каждая строка — отдельная тема."
    )
    duration = models.CharField(
        "Длительность", max_length=64, blank=True, help_text="Например: 2 недели"
    )
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)
    is_published = models.BooleanField("Опубликован", default=True)

    class Meta:
        verbose_name = "Модуль курса"
        verbose_name_plural = "Модули курса"
        ordering = ("order", "id")

    def __str__(self) -> str:
        return f"{self.order}. {self.title}"

    def topic_list(self) -> list[str]:
        return [line.strip() for line in self.topics.splitlines() if line.strip()]


class Lead(models.Model):
    """A marketing lead captured from the landing page (targeted ads)."""

    class Source(models.TextChoices):
        HERO = "hero", "Форма в первом экране"
        CONTACT = "contact", "Форма обратной связи"
        PRICING = "pricing", "Блок стоимости"
        OTHER = "other", "Другое"

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        CONTACTED = "contacted", "Связались"
        ENROLLED = "enrolled", "Записан"
        REJECTED = "rejected", "Отказ"

    name = models.CharField("Имя", max_length=120)
    phone = models.CharField("Телефон", max_length=32)
    email = models.EmailField("Email", blank=True)
    message = models.TextField("Комментарий", blank=True)
    source = models.CharField(
        "Источник", max_length=20, choices=Source.choices, default=Source.HERO
    )
    utm_source = models.CharField("UTM source", max_length=120, blank=True)
    utm_campaign = models.CharField("UTM campaign", max_length=120, blank=True)
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW, db_index=True
    )
    created_at = models.DateTimeField("Создана", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.name} — {self.phone} ({self.created_at:%d.%m.%Y})"
