from django.db import migrations

MODULES = [
    {
        "order": 1,
        "title": "Введение в программирование",
        "duration": "2 недели",
        "summary": "Разбираемся, как устроены программы и какие инструменты нужны разработчику. "
                   "Настраиваем рабочее окружение и пишем первые строки кода.",
        "topics": "Как работает компьютер и программы\nУстановка Python и редактора кода\n"
                  "Git и GitHub: первые коммиты\nПервая программа и её запуск",
    },
    {
        "order": 2,
        "title": "Основы Python",
        "duration": "3 недели",
        "summary": "Ключевой модуль курса: синтаксис, типы данных и логика программ. "
                   "Много практики на задачах.",
        "topics": "Переменные и типы данных\nУсловия и циклы\nФункции и модули\n"
                  "Списки, словари и множества\nРабота с файлами и исключениями",
    },
    {
        "order": 3,
        "title": "Объектно-ориентированное программирование",
        "duration": "2 недели",
        "summary": "Учимся проектировать код: классы, наследование и композиция. "
                   "Готовимся к работе с фреймворками.",
        "topics": "Классы и объекты\nИнкапсуляция и наследование\nМагические методы\n"
                  "Виртуальные окружения и зависимости",
    },
    {
        "order": 4,
        "title": "Базы данных и SQL",
        "duration": "2 недели",
        "summary": "Учимся хранить данные: от SQL-запросов до ORM. "
                   "Работаем с SQLite и PostgreSQL.",
        "topics": "Реляционная модель данных\nSQL: SELECT, INSERT, UPDATE, DELETE\n"
                  "Связи между таблицами\nDjango ORM и миграции",
    },
    {
        "order": 5,
        "title": "Веб-разработка на Django",
        "duration": "4 недели",
        "summary": "Создаём полноценный веб-сайт: маршрутизация, шаблоны, формы, "
                   "аутентификация и административная панель.",
        "topics": "Архитектура MVT в Django\nМаршрутизация и представления\n"
                  "Шаблоны и статика\nФормы и валидация\nАвторизация и роли пользователей\n"
                  "Административная панель",
    },
    {
        "order": 6,
        "title": "Финальный проект и портфолио",
        "duration": "2 недели",
        "summary": "Собираем всё вместе: проект в портфолио, деплой на сервер и подготовка "
                   "к собеседованию.",
        "topics": "Проектирование финального проекта\nДеплой на удалённый сервер\n"
                  "Оформление портфолио на GitHub\nПодготовка к техническому интервью",
    },
]


def seed_modules(apps, schema_editor):
    CourseModule = apps.get_model("courses", "CourseModule")
    for data in MODULES:
        CourseModule.objects.update_or_create(order=data["order"], defaults=data)


def unseed_modules(apps, schema_editor):
    CourseModule = apps.get_model("courses", "CourseModule")
    CourseModule.objects.filter(order__in=[m["order"] for m in MODULES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_modules, unseed_modules),
    ]
