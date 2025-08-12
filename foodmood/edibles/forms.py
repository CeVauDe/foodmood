from django import forms

from .models import Edible


class EdibleQuickForm(forms.ModelForm):
    """Minimal form to quickly create an Edible with just a name.

    Ingredients can be added/managed later from a dedicated edit page.
    """

    class Meta:
        model = Edible
        fields = ["name"]
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
