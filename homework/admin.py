from django.contrib import admin

from .models import Assignment, Review, Submission, SubmissionMessage


class ReviewInline(admin.StackedInline):
    model = Review
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    fields = ("reviewer", "score", "feedback", "created_at", "updated_at")


class MessageInline(admin.TabularInline):
    model = SubmissionMessage
    extra = 0
    fields = ("author", "body", "is_read", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "module", "max_score", "deadline", "is_published")
    list_filter = ("is_published", "module")
    list_editable = ("is_published",)
    search_fields = ("title", "description")
    ordering = ("order", "id")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "status", "submitted_at", "updated_at")
    list_filter = ("status", "assignment")
    search_fields = ("student__username", "student__last_name", "assignment__title")
    autocomplete_fields = ("student", "assignment")
    inlines = (ReviewInline, MessageInline)


@admin.register(SubmissionMessage)
class SubmissionMessageAdmin(admin.ModelAdmin):
    list_display = ("submission", "author", "short_body", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("body", "author__username", "submission__assignment__title")
    autocomplete_fields = ("submission", "author")

    @admin.display(description="Сообщение")
    def short_body(self, obj):
        return obj.body[:60]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("submission", "reviewer", "score", "updated_at")
    search_fields = ("submission__student__username", "submission__assignment__title", "feedback")
    autocomplete_fields = ("submission", "reviewer")
