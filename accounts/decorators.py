from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def teacher_required(view):
    """Allow access only to teachers/admins (and superusers)."""

    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_teacher:
            raise PermissionDenied("Доступ только для преподавателя.")
        return view(request, *args, **kwargs)

    return wrapper


def student_required(view):
    """Allow access only to students; teachers are redirected to their cabinet."""

    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_teacher:
            from django.shortcuts import redirect

            return redirect("dashboard:teacher")
        return view(request, *args, **kwargs)

    return wrapper
