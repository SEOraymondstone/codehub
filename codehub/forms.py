from django import forms


class StyledFormMixin:
    """Attach consistent CSS classes to every widget of a form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "checkbox-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "input select")
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", "input textarea")
                widget.attrs.setdefault("rows", 4)
            elif isinstance(widget, forms.HiddenInput):
                pass
            else:
                widget.attrs.setdefault("class", "input")
