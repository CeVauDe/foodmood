from typing import Any

from django import forms
from django.forms import ModelForm

from .models import Meal


class MealForm(ModelForm):
    """Form for creating and editing meals."""

    class Meta:
        model = Meal
        fields = ["name", "date_time", "recipes", "notes"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter meal name (e.g., Breakfast, Lunch)",
                }
            ),
            "date_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "recipes": forms.CheckboxSelectMultiple(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Any additional notes about this meal...",
                }
            ),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Make recipes optional but provide all available recipes
        self.fields["recipes"].required = False
        # Improve field labels and help text
        self.fields[
            "name"
        ].help_text = "Name your meal (e.g., 'Breakfast', 'Lunch', 'Snack')"
        self.fields["date_time"].help_text = "When did you eat this meal?"
        self.fields[
            "recipes"
        ].help_text = "Select any recipes that were part of this meal"
        self.fields["notes"].help_text = "Optional notes about the meal"
