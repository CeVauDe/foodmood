from typing import Any

import django.forms as forms
from django.forms import ModelChoiceField, inlineformset_factory
from django.utils import timezone

from .models import WellbeingCategory, WellbeingEntry, WellbeingOption


class CategoryForm(forms.ModelForm):
    class Meta:
        model = WellbeingCategory
        fields = ["name", "description", "icon"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "icon": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "😊"}
            ),
        }


class OptionForm(forms.ModelForm):
    """Form for creating/editing individual options for a category."""

    class Meta:
        model = WellbeingOption
        fields = ["label", "value", "color", "order"]
        widgets = {
            "label": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Excellent, 😊 Happy",
                }
            ),
            "value": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Numeric value for analysis",
                }
            ),
            "color": forms.Select(
                choices=[
                    ("", "Default"),
                    ("primary", "Blue"),
                    ("secondary", "Gray"),
                    ("success", "Green"),
                    ("info", "Cyan"),
                    ("warning", "Yellow"),
                    ("danger", "Red"),
                ],
                attrs={"class": "form-select"},
            ),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }


OptionFormSet = inlineformset_factory(
    WellbeingCategory,
    WellbeingOption,
    form=OptionForm,
    extra=3,  # Show 3 empty forms by default
    can_delete=True,
    min_num=2,  # Require at least 2 options
    validate_min=True,
)


class EntryForm(forms.ModelForm):
    """Full entry form with all fields."""

    class Meta:
        model = WellbeingEntry
        fields = ["category", "option", "recorded_at", "notes"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "option": forms.Select(attrs={"class": "form-select"}),
            "recorded_at": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # If category is pre-selected, filter options
        if "category" in self.data:
            try:
                category_id = int(self.data.get("category"))  # type: ignore[arg-type]
                option_field = self.fields["option"]
                assert isinstance(option_field, ModelChoiceField)
                option_field.queryset = WellbeingOption.objects.filter(
                    category_id=category_id
                ).order_by("order", "value")
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            option_field = self.fields["option"]
            assert isinstance(option_field, ModelChoiceField)
            option_field.queryset = self.instance.category.options.all()


class QuickEntryForm(forms.ModelForm):
    """Quick entry form for fast logging."""

    class Meta:
        model = WellbeingEntry
        fields = ["category", "option"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "option": forms.RadioSelect(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Auto-set recorded_at to now in view
        if "category" in self.data:
            try:
                category_id = int(self.data.get("category"))  # type: ignore[arg-type]
                option_field = self.fields["option"]
                assert isinstance(option_field, ModelChoiceField)
                option_field.queryset = WellbeingOption.objects.filter(
                    category_id=category_id
                ).order_by("order", "value")
            except (ValueError, TypeError):
                pass


class BulkEntryForm(forms.Form):
    """Form for logging multiple categories at once (daily check-in)."""

    recorded_at = forms.DateTimeField(
        initial=timezone.now,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Dynamically add a field for each active category
        categories = WellbeingCategory.objects.filter(is_active=True).prefetch_related(
            "options"
        )
        for category in categories:
            field_name = f"category_{category.pk}"
            self.fields[field_name] = forms.ModelChoiceField(
                queryset=category.options.all(),  # type: ignore[attr-defined]
                required=False,
                label=f"{category.icon} {category.name}"
                if category.icon
                else category.name,
                widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
                empty_label="Skip",
            )
