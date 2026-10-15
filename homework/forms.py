from django import forms
from django.conf import settings

from codehub.forms import StyledFormMixin
from codehub.utils import max_upload_label

from .models import Assignment, Review, Submission, SubmissionMessage


class SubmissionForm(StyledFormMixin, forms.ModelForm):
    comment = forms.CharField(
        label="Комментарий (необязательно)",
        required=False,
        max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4}),
        error_messages={"max_length": "Комментарий слишком длинный: максимум 2000 символов."},
    )

    class Meta:
        model = Submission
        fields = ("file", "comment")
        labels = {"file": "Файл с решением"}
        # FileInput, а не ClearableFileInput: тот подставлял прямую /media/-ссылку.
        widgets = {"file": forms.FileInput()}

    def clean_file(self):
        upload = self.cleaned_data["file"]
        if upload.size > settings.HOMEWORK_MAX_UPLOAD_SIZE:
            raise forms.ValidationError(f"Файл больше допустимых {max_upload_label()}.")
        return upload


class ReviewForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = ("score", "feedback")
        labels = {"score": "Балл", "feedback": "Обратная связь"}

    def clean_score(self):
        score = self.cleaned_data["score"]
        max_score = self.instance.submission.assignment.max_score
        if score > max_score:
            raise forms.ValidationError(f"Максимум по этому заданию — {max_score}.")
        return score


class AssignmentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ("module", "title", "description", "max_score", "deadline", "order", "is_published")
        widgets = {
            "deadline": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }
        labels = {"order": "Порядок выдачи"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["deadline"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"]


class MessageForm(StyledFormMixin, forms.ModelForm):
    """A single message in the student <-> teacher thread."""

    body = forms.CharField(
        label="",
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Напишите сообщение преподавателю…",
                "aria-label": "Текст сообщения",
            }
        ),
        error_messages={"max_length": "Сообщение слишком длинное: максимум 5000 символов."},
    )

    class Meta:
        model = SubmissionMessage
        fields = ("body",)

    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if not body:
            raise forms.ValidationError("Сообщение не может быть пустым.")
        return body

