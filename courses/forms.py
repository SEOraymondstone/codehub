from django import forms

from codehub.forms import StyledFormMixin

from .models import Lead


class LeadForm(StyledFormMixin, forms.ModelForm):
    """Lead capture form used for targeted advertising."""

    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        label="",
        help_text="Заполняется только ботами.",
    )
    message = forms.CharField(
        label="Комментарий",
        required=False,
        max_length=1000,
        widget=forms.Textarea(attrs={"rows": 3}),
        error_messages={"max_length": "Комментарий слишком длинный: максимум 1000 символов."},
    )

    class Meta:
        model = Lead
        fields = ("name", "phone", "email", "message")

    def clean_website(self):
        # Honeypot: a filled hidden field means an automated spam submission.
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Спам-защита сработала.")
        return ""

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Укажите имя.")
        return name
