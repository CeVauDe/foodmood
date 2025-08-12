from django import forms

from .models import Edible


class EdibleQuickForm(forms.ModelForm):
    """Create an Edible with a name and optional ingredients."""

    ingredients = forms.ModelMultipleChoiceField(
        queryset=Edible.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select",
                "data-placeholder": "Type to search ingredients",
            }
        ),
        help_text="Optionally select one or more existing edibles as ingredients.",
    )

    class Meta:
        model = Edible
        fields = ["name", "ingredients"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Avocado Toast",
                    "maxlength": 64,
                    "autofocus": True,
                }
            )
        }
        help_texts = {
            "name": "Give your edible a short, unique name (max 64 chars).",
        }
