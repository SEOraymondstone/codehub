from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.decorators import student_required, teacher_required
from courses.models import Lead
from homework.models import Assignment, Submission, SubmissionMessage

PENDING_STATUSES = (Submission.Status.SUBMITTED, Submission.Status.IN_REVIEW)
TEACHER_ROLES = ("teacher", "admin")


@login_required
def home(request):
    """Route an authenticated user to the correct cabinet."""
    if request.user.is_teacher:
        return redirect("dashboard:teacher")
    return redirect("dashboard:student")


@student_required
def student_dashboard(request):
    assignments = Assignment.objects.filter(is_published=True).select_related("module")
    submissions = {
        submission.assignment_id: submission
        for submission in Submission.objects.filter(student=request.user).select_related("review")
    }
    unread_ids = set(
        SubmissionMessage.objects.filter(submission__student=request.user, is_read=False)
        .exclude(author=request.user)
        .values_list("submission_id", flat=True)
    )

    rows = []
    reviewed = 0
    total_score = 0
    max_total = 0
    for assignment in assignments:
        submission = submissions.get(assignment.id)
        review = getattr(submission, "review", None) if submission else None
        if review:
            reviewed += 1
            total_score += review.score
            max_total += assignment.max_score
        rows.append(
            {
                "assignment": assignment,
                "submission": submission,
                "review": review,
                "is_overdue": assignment.deadline and assignment.deadline < timezone.now(),
                "has_unread": submission is not None and submission.pk in unread_ids,
            }
        )

    needs_revision = [
        row
        for row in rows
        if row["submission"] and row["submission"].status == Submission.Status.NEEDS_REVISION
    ]
    not_submitted = [row for row in rows if not row["submission"]]
    waiting = [
        row
        for row in rows
        if row["submission"] and row["submission"].status in PENDING_STATUSES
    ]

    focus = None
    if needs_revision:
        assignment = needs_revision[0]["assignment"]
        focus = {
            "tone": "danger",
            "title": f"Работа «{assignment.title}» на доработке",
            "text": "Откройте комментарий преподавателя, исправьте замечания и загрузите работу снова.",
            "url": reverse("homework:assignment_detail", args=[assignment.pk]),
            "label": "Открыть задание",
        }
    elif not_submitted:
        assignment = not_submitted[0]["assignment"]
        focus = {
            "tone": "action",
            "title": f"Следующий шаг — «{assignment.title}»",
            "text": "Загрузите файл с решением — преподаватель проверит его и пришлёт обратную связь.",
            "url": reverse("homework:assignment_detail", args=[assignment.pk]),
            "label": "Сдать задание",
        }
    elif waiting:
        focus = {
            "tone": "wait",
            "title": "Работы отправлены на проверку",
            "text": "Преподаватель скоро проверит их. Здесь появится балл и комментарий.",
            "url": reverse("homework:assignment_list"),
            "label": "Мои задания",
        }
    elif rows:
        focus = {
            "tone": "done",
            "title": "Все задания проверены",
            "text": "Отличная работа! Новые задания появятся здесь автоматически.",
            "url": None,
            "label": None,
        }

    context = {
        "rows": rows,
        "total": len(rows),
        "reviewed": reviewed,
        "pending": len(waiting),
        "not_submitted": len(not_submitted),
        "progress": round(reviewed / len(rows) * 100) if rows else 0,
        "score_sum": total_score,
        "score_max": max_total,
        "unread_total": len(unread_ids),
        "focus": focus,
    }
    return render(request, "dashboard/student.html", context)


@teacher_required
def teacher_dashboard(request):
    submissions = Submission.objects.select_related(
        "student", "assignment", "assignment__module", "review"
    )

    status = request.GET.get("status", "")
    if status in Submission.Status.values:
        submissions = submissions.filter(status=status)

    assignment_id = request.GET.get("assignment", "")
    if assignment_id.isdigit():
        submissions = submissions.filter(assignment_id=int(assignment_id))

    query = request.GET.get("q", "").strip()
    if query:
        from django.db.models import Q

        submissions = submissions.filter(
            Q(student__username__icontains=query)
            | Q(student__first_name__icontains=query)
            | Q(student__last_name__icontains=query)
            | Q(assignment__title__icontains=query)
        )

    unread_ids = set(
        SubmissionMessage.objects.filter(is_read=False)
        .exclude(author__role__in=TEACHER_ROLES)
        .exclude(author__is_superuser=True)
        .values_list("submission_id", flat=True)
    )

    stats = {
        "students": Submission.objects.values("student").distinct().count(),
        "submissions": Submission.objects.count(),
        "pending": Submission.objects.filter(status__in=PENDING_STATUSES).count(),
        "reviewed": Submission.objects.filter(status=Submission.Status.REVIEWED).count(),
        "leads_new": Lead.objects.filter(status=Lead.Status.NEW).count(),
    }

    next_pending = (
        Submission.objects.filter(status__in=PENDING_STATUSES)
        .select_related("student", "assignment")
        .order_by("submitted_at")
        .first()
    )

    context = {
        "submissions": submissions,
        "assignments": Assignment.objects.all(),
        "status_choices": Submission.Status.choices,
        "current_status": status,
        "current_assignment": assignment_id,
        "query": query,
        "stats": stats,
        "unread_ids": unread_ids,
        "unread_total": len(unread_ids),
        "next_pending": next_pending,
    }
    return render(request, "dashboard/teacher.html", context)
