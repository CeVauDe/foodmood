from typing import Any

from django import forms
from django.utils import timezone
from edibles.models import Edible

from .models import Meal


class MealForm(forms.ModelForm):
    """Create a Meal with title, category, eaten_at datetime, and optional edibles."""

    edibles = forms.ModelMultipleChoiceField(
        queryset=Edible.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select",
                "data-placeholder": "Type to search edibles",
                "placeholder": "Type to search edibles",
            }
        ),
        help_text="Optionally select one or more edibles for this meal.",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Move help text into tooltip attributes on the widgets
        for name, field in self.fields.items():
            if field.help_text:
                field.widget.attrs.setdefault("title", field.help_text)
                field.widget.attrs.setdefault("data-bs-toggle", "tooltip")
                field.widget.attrs.setdefault("data-bs-placement", "top")

        # Pre-fill eaten_at with current datetime if creating a new meal
        if not self.instance.pk and "eaten_at" in self.fields:
            self.initial["eaten_at"] = timezone.now().strftime("%Y-%m-%dT%H:%M")

    class Meta:
        model = Meal
        fields = ["title", "category", "eaten_at", "edibles"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Breakfast with Toast",
                    "maxlength": 128,
                    "autofocus": True,
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "eaten_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }
        help_texts = {
            "title": "Give your meal a descriptive title (max 128 chars).",
            "category": "Select the meal category (Breakfast, Lunch, Dinner, or Snack).",
            "eaten_at": "When did you eat this meal?",
        }
