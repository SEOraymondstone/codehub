from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm, SignUpForm, StudentProfileForm
from .models import StudentProfile


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        StudentProfile.objects.get_or_create(user=user)
        login(request, user)
        messages.success(request, "Добро пожаловать в CodeHub! Личный кабинет активирован.")
        return redirect("dashboard:home")

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    user_form = ProfileForm(instance=request.user)
    profile_form = StudentProfileForm(instance=student_profile)

    if request.method == "POST":
        # На странице две независимые формы. Сохраняем только ту, которую
        # отправили, иначе вторая форма затрёт чужие поля пустыми значениями.
        if "save_account" in request.POST:
            user_form = ProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Данные аккаунта сохранены.")
                return redirect("accounts:profile")
            messages.error(request, "Исправьте ошибки в блоке «Аккаунт».")
        elif "save_study" in request.POST:
            profile_form = StudentProfileForm(request.POST, instance=student_profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Данные об обучении сохранены.")
                return redirect("accounts:profile")
            messages.error(request, "Исправьте ошибки в блоке «Обучение».")
        else:
            messages.error(request, "Не удалось определить форму. Попробуйте ещё раз.")

    return render(
        request,
        "accounts/profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )
