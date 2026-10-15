"""Create demo CodeHub data: teacher, student, assignments and a sample work.

Usage:
    python manage.py seed_codehub
    python manage.py seed_codehub --with-demo-work
"""

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from courses.models import CourseModule, Lead
from homework.models import Assignment, Submission

User = get_user_model()

TEACHER = {
    "username": "teacher",
    "password": "teacher12345",
    "first_name": "Алексей",
    "last_name": "Преподавателев",
    "email": "teacher@codehub.dev",
    "role": User.Role.TEACHER,
    "telegram": "@codehub_teacher",
}

STUDENT = {
    "username": "student",
    "password": "student12345",
    "first_name": "Мария",
    "last_name": "Студентова",
    "email": "student@codehub.dev",
    "role": User.Role.STUDENT,
    "telegram": "@codehub_student",
}

ASSIGNMENTS = [
    {
        "order": 1,
        "title": "ДЗ №1. Первая программа и Git",
        "module_order": 1,
        "max_score": 100,
        "summary": (
            "Установите Python, создайте репозиторий на GitHub и загрузите скрипт, "
            "который выводит приветствие и текущую дату. Приложите ссылку на репозиторий "
            "в комментарии к работе."
        ),
    },
    {
        "order": 2,
        "title": "ДЗ №2. Функции и структуры данных",
        "module_order": 2,
        "max_score": 100,
        "summary": (
            "Напишите набор функций для работы со списком задач: добавление, удаление, "
            "поиск и сортировка. Покройте каждую функцию коротким примером использования."
        ),
    },
    {
        "order": 3,
        "title": "ДЗ №3. Классы и наследование",
        "module_order": 3,
        "max_score": 100,
        "summary": (
            "Спроектируйте иерархию классов для небольшой библиотеки: базовый класс, "
            "наследники и перегрузка магических методов."
        ),
    },
    {
        "order": 4,
        "title": "ДЗ №4. Запросы к базе данных",
        "module_order": 4,
        "max_score": 100,
        "summary": (
            "Спроектируйте схему из трёх связанных таблиц и напишите SQL-запросы для "
            "выборки, обновления и удаления данных."
        ),
    },
    {
        "order": 5,
        "title": "ДЗ №5. Первое Django-приложение",
        "module_order": 5,
        "max_score": 100,
        "summary": (
            "Создайте Django-проект с одним приложением, двумя маршрутами и шаблоном. "
            "Загрузите архив проекта или ссылку на репозиторий."
        ),
    },
    {
        "order": 6,
        "title": "Финальный проект",
        "module_order": 6,
        "max_score": 200,
        "summary": (
            "Соберите итоговый проект: веб-приложение на Django с базой данных, "
            "авторизацией и развёртыванием на сервере. Подготовьте README."
        ),
    },
]


class Command(BaseCommand):
    help = "Создаёт демонстрационные данные CodeHub (пользователи, задания, работа)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-demo-work",
            action="store_true",
            help="Добавить пример загруженной работы студента.",
        )

    def handle(self, *args, **options):
        teacher = self._ensure_user(TEACHER)
        student = self._ensure_user(STUDENT)

        modules = {module.order: module for module in CourseModule.objects.all()}
        created_assignments = 0
        for data in ASSIGNMENTS:
            module = modules.get(data["module_order"])
            _, created = Assignment.objects.update_or_create(
                title=data["title"],
                defaults={
                    "order": data["order"],
                    "description": data["summary"],
                    "max_score": data["max_score"],
                    "module": module,
                    "is_published": True,
                },
            )
            created_assignments += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово. Преподаватель: {teacher.username}/{TEACHER['password']}, "
                f"студент: {student.username}/{STUDENT['password']}, "
                f"новых заданий: {created_assignments}."
            )
        )

        if options["with_demo_work"]:
            self._create_demo_work(student)

        if not Lead.objects.exists():
            Lead.objects.create(
                name="Иван",
                phone="+7 (999) 123-45-67",
                email="ivan@example.com",
                message="Хочу узнать про ближайший поток.",
                source=Lead.Source.HERO,
                utm_source="yandex",
                utm_campaign="codehub-search",
            )
            self.stdout.write("Добавлена демонстрационная заявка.")

    def _ensure_user(self, data):
        username = data["username"]
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "email": data["email"],
                "role": data["role"],
                "telegram": data.get("telegram", ""),
            },
        )
        if created:
            user.set_password(data["password"])
            user.save()
            self.stdout.write(f"Создан пользователь {username}.")
        else:
            self.stdout.write(f"Пользователь {username} уже существует.")
        return user

    def _create_demo_work(self, student):
        assignment = Assignment.objects.order_by("order").first()
        if not assignment:
            return
        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            student=student,
            defaults={
                "comment": "Ссылка на репозиторий: https://github.com/example/homework-1",
                "status": Submission.Status.SUBMITTED,
            },
        )
        if created and not submission.file:
            submission.file.save(
                "demo_solution.py",
                ContentFile(b'print("Hello, CodeHub!")\n'),
                save=True,
            )
            self.stdout.write("Добавлена демонстрационная работа студента.")
