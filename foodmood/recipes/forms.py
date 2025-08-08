import json

from django import forms
from django.forms import ModelForm
from django.utils import timezone

from .models import Ingredient, Recipe, RecipeIngredient


class RecipeForm(ModelForm):
    """Form for creating and editing recipes with dynamic ingredient management."""

    # Ingredient selection dropdown for adding ingredients one by one
    add_ingredient = forms.ModelChoiceField(
        queryset=Ingredient.objects.all(),
        required=False,
        empty_label="Select an ingredient to add...",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "add-ingredient-select",
            }
        ),
        help_text="Select an ingredient to add to this recipe",
    )

    # Weight field for the selected ingredient
    ingredient_weight = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Weight in grams",
                "step": "0.01",
                "min": "0",
                "id": "ingredient-weight-input",
            }
        ),
        help_text="Weight of the ingredient in grams",
    )

    # Hidden field to store the ingredients data as JSON
    ingredients_data = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"id": "ingredients-data"}),
        help_text="Internal field to store ingredients data",
    )

    class Meta:
        model = Recipe
        fields = ["name", "notes"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter recipe name",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Optional recipe notes or instructions",
                }
            ),
        }
        help_texts = {
            "name": "What would you like to call this recipe?",
            "notes": "Any additional notes, instructions, or comments about this recipe",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        """Custom validation and data processing."""
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        """Override save to handle creation_date field."""
        recipe = super().save(commit=False)

        # Set creation_date to current time when saving
        recipe.creation_date = timezone.now()

        if commit:
            recipe.save()
            # Handle ingredients after recipe is saved
            self._save_ingredients(recipe)

        return recipe

    def _save_ingredients(self, recipe):
        """Handle saving the ingredients from the ingredients_data field."""
        # Clear existing ingredients
        recipe.ingredients.clear()

        # Process ingredients_data if provided
        ingredients_json = self.cleaned_data.get("ingredients_data", "")
        if ingredients_json:
            try:
                ingredients_list = json.loads(ingredients_json)
                for ingredient_data in ingredients_list:
                    ingredient_id = ingredient_data.get("id")
                    weight = ingredient_data.get("weight")

                    if ingredient_id:
                        try:
                            ingredient = Ingredient.objects.get(id=ingredient_id)
                            RecipeIngredient.objects.create(
                                recipe=recipe,
                                ingredient=ingredient,
                                weight_g=weight if weight else None,
                                notes="",  # No per-ingredient notes
                            )
                        except Ingredient.DoesNotExist:
                            continue  # Skip invalid ingredients
            except (json.JSONDecodeError, KeyError):
                pass  # Handle malformed JSON gracefully
