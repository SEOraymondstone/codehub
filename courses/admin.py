from django.contrib import admin

from .models import CourseModule, Lead


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "duration", "is_published")
    list_editable = ("is_published",)
    list_filter = ("is_published",)
    search_fields = ("title", "summary", "topics")
    ordering = ("order", "id")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "source", "status", "created_at")
    list_filter = ("status", "source", "created_at")
    search_fields = ("name", "phone", "email", "message")
    list_editable = ("status",)
    readonly_fields = ("created_at", "utm_source", "utm_campaign")
    date_hierarchy = "created_at"
    actions = ("mark_contacted", "mark_enrolled")

    @admin.action(description="Отметить как «Связались»")
    def mark_contacted(self, request, queryset):
        updated = queryset.update(status=Lead.Status.CONTACTED)
        self.message_user(request, f"Обновлено заявок: {updated}")

    @admin.action(description="Отметить как «Записаны»")
    def mark_enrolled(self, request, queryset):
        updated = queryset.update(status=Lead.Status.ENROLLED)
        self.message_user(request, f"Обновлено заявок: {updated}")
