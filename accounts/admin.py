from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import StudentProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username", "email", "first_name", "last_name",
        "role", "is_staff", "is_active", "date_joined",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name", "phone", "telegram")
    ordering = ("-date_joined",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("CodeHub", {"fields": ("role", "phone", "telegram", "bio")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("CodeHub", {"fields": ("role", "email", "first_name", "last_name", "phone")}),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "level", "goal", "enrolled_at")
    list_filter = ("level",)
    search_fields = ("user__username", "user__email", "user__last_name")
    autocomplete_fields = ("user",)
