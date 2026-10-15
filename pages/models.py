from django.db import models


class SiteSettings(models.Model):
    """Singleton с основными текстами и контактами сайта.

    Редактируется в админке, поэтому менять заголовки, цену и контакты можно
    без правки кода.
    """

    name = models.CharField("Название проекта", max_length=100, default="CodeHub")
    tagline = models.TextField(
        "Краткое описание",
        default="Онлайн-курс по программированию: от нуля до первого оффера",
    )
    hero_title = models.CharField(
        "Заголовок первого экрана",
        max_length=200,
        default="Программирование, которое",
    )
    hero_accent = models.CharField(
        "Выделенная часть заголовка",
        max_length=200,
        default="понятно вашему ребёнку",
        blank=True,
    )
    hero_subtitle = models.TextField(
        "Подзаголовок первого экрана",
        default=(
            "Занятия в удобном темпе, домашние задания с проверкой преподавателем "
            "и понятная обратная связь для ученика и родителей."
        ),
        blank=True,
    )
    price_from = models.CharField("Цена «от»", max_length=32, default="$100")
    phone = models.CharField("Телефон", max_length=32, default="+7 (900) 000-00-00")
    phone_secondary = models.CharField(
        "Дополнительный телефон", max_length=32, default="+7 (900) 111-11-11", blank=True
    )
    email = models.EmailField("Email", default="hello@codehub.dev", blank=True)
    telegram = models.URLField("Telegram", blank=True, default="https://t.me/codehub")
    whatsapp = models.URLField("WhatsApp", blank=True, default="https://wa.me/79000000000")
    instagram = models.URLField("Instagram", blank=True, default="https://instagram.com/codehub")
    youtube = models.URLField("YouTube", blank=True, default="https://youtube.com/@codehub")
    github = models.URLField("GitHub", blank=True, default="https://github.com/codehub")
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self) -> str:
        return self.name or "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):  # pragma: no cover - защита синглтона
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "tagline": self.tagline,
            "hero_title": self.hero_title,
            "hero_accent": self.hero_accent,
            "hero_subtitle": self.hero_subtitle,
            "price_from": self.price_from,
            "phone": self.phone,
            "phone_secondary": self.phone_secondary,
            "email": self.email,
            "telegram": self.telegram,
            "whatsapp": self.whatsapp,
            "instagram": self.instagram,
            "youtube": self.youtube,
            "github": self.github,
        }


class OrderedPublished(models.Model):
    """Общая база для блоков сайта: порядок вывода и публикация."""

    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)
    is_published = models.BooleanField("Опубликовано", default=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ("order", "id")


class StatItem(OrderedPublished):
    value = models.CharField("Значение", max_length=32, help_text="Например: 6 или 24/7")
    label = models.CharField("Подпись", max_length=120)

    class Meta(OrderedPublished.Meta):
        verbose_name = "Цифра на первом экране"
        verbose_name_plural = "Цифры на первом экране"

    def __str__(self) -> str:
        return f"{self.value} — {self.label}"


class Advantage(OrderedPublished):
    icon = models.CharField("Иконка/номер", max_length=8, blank=True, default="01")
    title = models.CharField("Заголовок", max_length=160)
    text = models.TextField("Текст")

    class Meta(OrderedPublished.Meta):
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"

    def __str__(self) -> str:
        return self.title


class PricingPlan(OrderedPublished):
    name = models.CharField("Название тарифа", max_length=120)
    price = models.CharField("Цена", max_length=32)
    period = models.CharField("Период", max_length=64, default="единоразово за курс", blank=True)
    features = models.TextField("Что входит (по одному пункту в строке)")
    button_text = models.CharField("Текст кнопки", max_length=64, default="Записаться")
    is_featured = models.BooleanField("Выделить тариф", default=False)
    badge = models.CharField("Плашка", max_length=64, blank=True, default="Выбирают чаще")

    class Meta(OrderedPublished.Meta):
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self) -> str:
        return f"{self.name} — {self.price}"

    def feature_list(self) -> list[str]:
        return [line.strip() for line in self.features.splitlines() if line.strip()]


class Teacher(OrderedPublished):
    name = models.CharField("Имя", max_length=120)
    title = models.CharField("Должность", max_length=160, blank=True)
    bio = models.TextField("О преподавателе", blank=True)
    photo = models.ImageField("Фото", upload_to="teachers/", blank=True, null=True)

    class Meta(OrderedPublished.Meta):
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"

    def __str__(self) -> str:
        return self.name

    def initials(self) -> str:
        parts = [part for part in self.name.split() if part]
        return "".join(part[0].upper() for part in parts[:2]) or "?"


class Testimonial(OrderedPublished):
    author = models.CharField("Автор", max_length=120)
    role = models.CharField("Кто он", max_length=160, blank=True, default="Родитель ученика")
    text = models.TextField("Отзыв")

    class Meta(OrderedPublished.Meta):
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self) -> str:
        return f"{self.author}: {self.text[:40]}"


class FAQItem(OrderedPublished):
    question = models.CharField("Вопрос", max_length=240)
    answer = models.TextField("Ответ")

    class Meta(OrderedPublished.Meta):
        verbose_name = "Вопрос и ответ"
        verbose_name_plural = "Частые вопросы"

    def __str__(self) -> str:
        return self.question


class ContactMessage(models.Model):
    """Free-form message sent through the public contacts block."""

    name = models.CharField("Имя", max_length=120)
    email = models.EmailField("Email")
    subject = models.CharField("Тема", max_length=200, blank=True)
    message = models.TextField("Сообщение")
    is_processed = models.BooleanField("Обработано", default=False, db_index=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Сообщение с сайта"
        verbose_name_plural = "Сообщения с сайта"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.name} <{self.email}> — {self.created_at:%d.%m.%Y}"
