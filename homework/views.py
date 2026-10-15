import logging
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Avg, Count
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import teacher_required
from courses.models import CourseModule

from .forms import AssignmentForm, MessageForm, ReviewForm, SubmissionForm
from .models import Assignment, Review, Submission, SubmissionMessage

logger = logging.getLogger(__name__)

PENDING_STATUSES = (Submission.Status.SUBMITTED, Submission.Status.IN_REVIEW)
TEACHER_ROLES = ("teacher", "admin")


def _send_mail_safe(subject: str, message: str, recipients: list[str]) -> None:
    """Send a notification without ever breaking the request/response cycle."""
    recipients = [address for address in recipients if address]
    if not recipients:
        return
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
    except Exception:  # pragma: no cover - depends on the configured mailer
        logger.exception("Не удалось отправить письмо CodeHub")


def _notify_teacher(submission: Submission) -> None:
    _send_mail_safe(
        subject=f"CodeHub: новая работа — {submission.assignment.title}",
        message=(
            f"Студент {submission.student.display_name} загрузил работу "
            f"по заданию «{submission.assignment.title}»."
        ),
        recipients=[settings.TEACHER_NOTIFICATION_EMAIL],
    )


def _notify_counterpart(submission: Submission, author, body: str) -> None:
    """Notify the other side of the thread about a new message."""
    if author == submission.student:
        subject = f"CodeHub: вопрос по работе — {submission.assignment.title}"
        recipients = [settings.TEACHER_NOTIFICATION_EMAIL]
    else:
        subject = f"CodeHub: новое сообщение по работе — {submission.assignment.title}"
        recipients = [submission.student.email]
    _send_mail_safe(subject=subject, message=body, recipients=recipients)


def _unread_ids_for_teacher() -> set[int]:
    """Submission ids that have unread messages written by students."""
    return set(
        SubmissionMessage.objects.filter(is_read=False)
        .exclude(author__role__in=TEACHER_ROLES)
        .exclude(author__is_superuser=True)
        .values_list("submission_id", flat=True)
    )


def _next_pending_submission(exclude_pk: int | None = None) -> Submission | None:
    queryset = (
        Submission.objects.filter(status__in=PENDING_STATUSES)
        .select_related("student", "assignment")
        .order_by("submitted_at")
    )
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)
    return queryset.first()


# --------------------------------------------------------------------------
# Student side
# --------------------------------------------------------------------------
@login_required
def assignment_list(request):
    if request.user.is_teacher:
        return redirect("homework:manage_assignments")

    assignments = Assignment.objects.filter(is_published=True).select_related("module")
    submissions = {
        s.assignment_id: s
        for s in Submission.objects.filter(student=request.user).select_related("review")
    }
    unread_ids = set(
        SubmissionMessage.objects.filter(submission__student=request.user, is_read=False)
        .exclude(author=request.user)
        .values_list("submission_id", flat=True)
    )
    items = [
        {
            "assignment": assignment,
            "submission": submissions.get(assignment.id),
            "has_unread": submissions.get(assignment.id) is not None
            and submissions[assignment.id].pk in unread_ids,
        }
        for assignment in assignments
    ]
    return render(
        request,
        "homework/assignment_list.html",
        {"items": items, "unread_total": len(unread_ids)},
    )


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.user.is_teacher:
        return redirect("homework:submission_list")
    if not assignment.is_published:
        messages.error(request, "Это задание ещё не опубликовано.")
        return redirect("homework:assignment_list")

    submission = (
        Submission.objects.filter(assignment=assignment, student=request.user)
        .select_related("review")
        .first()
    )
    form = SubmissionForm(instance=submission)

    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            new_submission = form.save(commit=False)
            new_submission.assignment = assignment
            new_submission.student = request.user
            new_submission.status = Submission.Status.SUBMITTED
            new_submission.save()
            # Re-open the grade once the work is updated.
            Review.objects.filter(submission=new_submission).delete()
            messages.success(request, "Работа загружена и отправлена на проверку.")
            _notify_teacher(new_submission)
            return redirect("homework:assignment_detail", pk=assignment.pk)
        messages.error(request, "Не удалось загрузить работу. Проверьте файл.")

    if submission:
        # Replies from the teacher are read as soon as the student opens the page.
        submission.messages.exclude(author=request.user).update(is_read=True)

    return render(
        request,
        "homework/assignment_detail.html",
        {
            "assignment": assignment,
            "submission": submission,
            "form": form,
            "thread_messages": submission.messages.select_related("author") if submission else [],
            "message_form": MessageForm(),
        },
    )


@login_required
def post_message(request, pk):
    """Add a message to the student <-> teacher thread of a submission."""
    submission = get_object_or_404(
        Submission.objects.select_related("student", "assignment"), pk=pk
    )
    is_owner = request.user == submission.student
    if not (is_owner or request.user.is_teacher):
        raise PermissionDenied("Нет доступа к этой работе.")

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.submission = submission
            message.author = request.user
            message.save()
            _notify_counterpart(submission, request.user, message.body)
            messages.success(request, "Сообщение отправлено.")
        else:
            messages.error(request, "Введите текст сообщения.")

    if is_owner:
        return redirect("homework:assignment_detail", pk=submission.assignment_id)
    return redirect("homework:submission_detail", pk=submission.pk)


@login_required
def download_submission(request, pk):
    """Отдаём файл работы только её автору или преподавателю.

    Прямые ссылки на /media/submissions/ закрыты, чтобы студенты не могли
    скачать чужие решения.
    """
    submission = get_object_or_404(Submission.objects.select_related("student"), pk=pk)
    if not (request.user == submission.student or request.user.is_teacher):
        raise PermissionDenied("Нет доступа к файлу работы.")
    if not submission.file:
        raise Http404("Файл не найден.")
    return FileResponse(
        submission.file.open("rb"),
        as_attachment=True,
        filename=Path(submission.file.name).name,
    )


# --------------------------------------------------------------------------
# Teacher side
# --------------------------------------------------------------------------
@teacher_required
def submission_list(request):
    submissions = Submission.objects.select_related(
        "student", "assignment", "review"
    ).order_by("-submitted_at")
    status = request.GET.get("status", "")
    if status in Submission.Status.values:
        submissions = submissions.filter(status=status)
    return render(
        request,
        "homework/submission_list.html",
        {
            "submissions": submissions,
            "status_choices": Submission.Status.choices,
            "current_status": status,
            "unread_ids": _unread_ids_for_teacher(),
            "next_pending": _next_pending_submission(),
        },
    )


@teacher_required
def submission_detail(request, pk):
    submission = get_object_or_404(
        Submission.objects.select_related("student", "assignment", "assignment__module"), pk=pk
    )
    review = getattr(submission, "review", None)
    instance = review or Review(submission=submission)
    form = ReviewForm(instance=instance, prefix="review")

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=instance, prefix="review")
        if form.is_valid():
            review = form.save(commit=False)
            review.submission = submission
            review.reviewer = request.user
            review.save()

            new_status = request.POST.get("status", Submission.Status.REVIEWED)
            if new_status not in Submission.Status.values:
                new_status = Submission.Status.REVIEWED
            submission.status = new_status
            submission.save(update_fields=["status", "updated_at"])

            # Преподаватель уже увидел работу — закрываем вопросы студента,
            # в том числе при переходе к следующей работе.
            submission.messages.filter(author=submission.student).update(is_read=True)

            message = (
                f"Здравствуйте, {submission.student.display_name}!\n\n"
                f"Задание: {submission.assignment.title}\n"
                f"Балл: {review.score} из {submission.assignment.max_score}\n\n"
                f"Комментарий преподавателя:\n{review.feedback}"
            )
            _send_mail_safe(
                subject=f"CodeHub: работа проверена — {submission.assignment.title}",
                message=message,
                recipients=[submission.student.email],
            )
            messages.success(request, "Проверка сохранена, студент получил обратную связь.")

            # One-click workflow: jump straight to the next work in the queue.
            if request.POST.get("next_submission"):
                next_submission = _next_pending_submission(exclude_pk=submission.pk)
                if next_submission:
                    return redirect("homework:submission_detail", pk=next_submission.pk)
                messages.info(request, "Очередь проверки пуста — все работы проверены.")
            return redirect("homework:submission_detail", pk=submission.pk)
        messages.error(request, "Исправьте ошибки в форме проверки.")

    # Student messages are read as soon as the teacher opens the work.
    submission.messages.filter(author=submission.student).update(is_read=True)

    return render(
        request,
        "homework/submission_detail.html",
        {
            "submission": submission,
            "review": review,
            "form": form,
            "status_choices": Submission.Status.choices,
            "thread_messages": submission.messages.select_related("author"),
            "message_form": MessageForm(),
            "next_pending": _next_pending_submission(exclude_pk=submission.pk),
        },
    )


@teacher_required
def manage_assignments(request):
    assignments = Assignment.objects.select_related("module").annotate(
        submission_total=Count("submissions"), average_score=Avg("submissions__review__score")
    )
    return render(
        request,
        "homework/manage_assignments.html",
        {"assignments": assignments, "modules_total": CourseModule.objects.count()},
    )


@teacher_required
def assignment_create(request):
    form = AssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        assignment = form.save()
        messages.success(request, f"Задание «{assignment.title}» создано.")
        return redirect("homework:manage_assignments")
    return render(
        request,
        "homework/assignment_form.html",
        {"form": form, "title": "Новое задание"},
    )


@teacher_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    form = AssignmentForm(request.POST or None, instance=assignment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Задание обновлено.")
        return redirect("homework:manage_assignments")
    return render(
        request,
        "homework/assignment_form.html",
        {"form": form, "title": f"Редактирование: {assignment.title}", "assignment": assignment},
    )
