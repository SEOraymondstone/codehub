from django.db import migrations

SETTINGS = {
    "name": "CodeHub",
    "tagline": "Онлайн-курс по программированию: от нуля до первого оффера",
    "hero_title": "Программирование, которое",
    "hero_accent": "понятно вашему ребёнку",
    "hero_subtitle": (
        "Занятия в удобном темпе, домашние задания с проверкой преподавателем "
        "и понятная обратная связь для ученика и родителей."
    ),
    "price_from": "$100",
    "phone": "+7 (900) 000-00-00",
    "phone_secondary": "+7 (900) 111-11-11",
    "email": "hello@codehub.dev",
    "telegram": "https://t.me/codehub",
    "whatsapp": "https://wa.me/79000000000",
    "instagram": "https://instagram.com/codehub",
    "youtube": "https://youtube.com/@codehub",
    "github": "https://github.com/codehub",
}

STATS = [
    ("6", "модулей программы"),
    ("24/7", "доступ к личному кабинету"),
    ("1:1", "проверка ДЗ преподавателем"),
    ("10", "учеников в группе"),
]

ADVANTAGES = [
    ("01", "Практика с первого урока", "Ученик сразу пишет код, а не только смотрит теорию. Каждый модуль закрепляется заданием."),
    ("02", "Личный кабинет ученика", "Загрузка домашних заданий, статус проверки и баллы — всё в одном месте, доступно 24/7."),
    ("03", "Обратная связь по каждой работе", "Преподаватель разбирает решение и пишет рекомендации: что получилось и что улучшить."),
    ("04", "Спокойный темп", "Занятия два раза в неделю и записи уроков — можно пересмотреть сложную тему в любое время."),
]

PLANS = [
    {
        "name": "Старт",
        "price": "$100",
        "period": "единоразово за курс",
        "features": "Доступ к программе курса\nЛичный кабинет ученика\nПроверка домашних заданий\nЧат с преподавателем",
        "button_text": "Оставить заявку",
        "is_featured": False,
    },
    {
        "name": "Практика",
        "price": "$180",
        "period": "единоразово за курс",
        "features": "Всё из тарифа «Старт»\nИндивидуальные созвоны с преподавателем\nРазбор кода ученика\nПомощь с портфолио",
        "button_text": "Записаться",
        "is_featured": True,
        "badge": "Выбирают чаще",
    },
    {
        "name": "Наставничество",
        "price": "$300",
        "period": "единоразово за курс",
        "features": "Всё из тарифа «Практика»\nПодготовка к собеседованиям\nСопровождение до первого оффера\nРазбор тестовых заданий",
        "button_text": "Обсудить",
        "is_featured": False,
    },
]

TEACHERS = [
    {
        "name": "Алексей Преподавателев",
        "title": "Преподаватель Python и Django",
        "bio": (
            "8 лет в разработке и 4 года преподавания. Объясняет сложные вещи простым языком, "
            "разбирает код каждого ученика и помогает дойти до первого проекта в портфолио."
        ),
    },
]

TESTIMONIALS = [
    {"author": "Мария К.", "role": "мама ученика, 12 лет", "text": "Сын ждал занятия и сам просил помочь с домашкой. Отдельное спасибо за понятные комментарии преподавателя."},
    {"author": "Дмитрий П.", "role": "студент курса", "text": "Начинал с нуля. Через полгода сделал свой первый сайт на Django и прошёл собеседование на стажировку."},
    {"author": "Ольга С.", "role": "мама ученика, 15 лет", "text": "Удобно, что видно прогресс и баллы. Ребёнок стал самостоятельнее и увереннее."},
]

FAQ = [
    ("Нужен ли ребёнку опыт в программировании?", "Нет. Курс рассчитан на старт с нуля: сначала знакомимся с компьютером и первыми программами, затем переходим к более сложным темам."),
    ("С какого возраста можно заниматься?", "Оптимально с 10–11 лет: ребёнок уверенно читает и работает с компьютером. Для взрослых новичков программа тоже подходит."),
    ("Как родители смогут следить за результатом?", "В личном кабинете видны сданные работы, баллы и комментарии преподавателя. Дополнительно мы сообщаем о прогрессе по запросу."),
    ("Что если ученик пропустил урок?", "Запись урока и материалы остаются в доступе. Преподаватель поможет догнать программу и ответит на вопросы в чате."),
    ("Какое оборудование нужно?", "Достаточно ноутбука или компьютера с интернетом. Всё программное обеспечение бесплатное, поможем с установкой на первом уроке."),
]


def seed(apps, schema_editor):
    SiteSettings = apps.get_model("pages", "SiteSettings")
    StatItem = apps.get_model("pages", "StatItem")
    Advantage = apps.get_model("pages", "Advantage")
    PricingPlan = apps.get_model("pages", "PricingPlan")
    Teacher = apps.get_model("pages", "Teacher")
    Testimonial = apps.get_model("pages", "Testimonial")
    FAQItem = apps.get_model("pages", "FAQItem")

    SiteSettings.objects.update_or_create(pk=1, defaults=SETTINGS)

    for order, (value, label) in enumerate(STATS, start=1):
        StatItem.objects.update_or_create(order=order, defaults={"value": value, "label": label})

    for order, (icon, title, text) in enumerate(ADVANTAGES, start=1):
        Advantage.objects.update_or_create(title=title, defaults={"order": order, "icon": icon, "text": text})

    for order, plan in enumerate(PLANS, start=1):
        PricingPlan.objects.update_or_create(
            name=plan["name"], defaults={**plan, "order": order}
        )

    for order, teacher in enumerate(TEACHERS, start=1):
        Teacher.objects.update_or_create(name=teacher["name"], defaults={**teacher, "order": order})

    for order, review in enumerate(TESTIMONIALS, start=1):
        Testimonial.objects.update_or_create(
            author=review["author"], defaults={**review, "order": order}
        )

    for order, (question, answer) in enumerate(FAQ, start=1):
        FAQItem.objects.update_or_create(
            question=question, defaults={"answer": answer, "order": order}
        )


def unseed(apps, schema_editor):
    for model_name in (
        "StatItem", "Advantage", "PricingPlan", "Teacher", "Testimonial", "FAQItem", "SiteSettings"
    ):
        apps.get_model("pages", model_name).objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0002_advantage_faqitem_pricingplan_sitesettings_statitem_and_more"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
