from django import forms

from codehub.forms import StyledFormMixin

from .models import ContactMessage


class ContactForm(StyledFormMixin, forms.ModelForm):
    subject = forms.CharField(
        label="Тема", required=False, max_length=200,
        error_messages={"max_length": "Тема слишком длинная: максимум 200 символов."},
    )
    message = forms.CharField(
        label="Сообщение",
        max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4}),
        error_messages={"max_length": "Сообщение слишком длинное: максимум 2000 символов."},
    )

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")
