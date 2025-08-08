from datetime import datetime
from typing import Any

from django import forms
from django.forms import ModelForm
from django.utils import timezone

from .models import Ingredient, Meal, Recipe, RecipeIngredient


class MealForm(ModelForm):
    """Form for creating and editing meals."""

    # Add separate date and time fields for better UX
    meal_date = forms.DateField(
        required=False,  # Make optional since clean() method handles defaults
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        help_text="What date did you eat this meal?",
    )

    meal_time = forms.TimeField(
        required=False,  # Make optional since clean() method handles defaults
        widget=forms.TimeInput(
            attrs={
                "class": "form-control",
                "type": "time",
                "step": "60",  # Only allow hour and minute selection (no seconds)
            }
        ),
        help_text="What time did you eat this meal?",
    )

    # Recipe selection dropdown for adding recipes one by one
    add_recipe = forms.ModelChoiceField(
        queryset=Recipe.objects.all(),
        required=False,
        empty_label="Select a recipe to add...",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "add-recipe-select",
            }
        ),
        help_text="Select a recipe to add to this meal",
    )

    class Meta:
        model = Meal
        fields = ["name", "recipes", "notes"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter meal name (e.g., Breakfast, Lunch)",
                }
            ),
            "recipes": forms.MultipleHiddenInput(),  # Hidden field to store selected recipes
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Any additional notes about this meal...",
                }
            ),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Extract initial datetime if provided
        initial_datetime = None
        if "initial" in kwargs and "date_time" in kwargs["initial"]:
            initial_datetime = kwargs["initial"]["date_time"]
            # Set separate date and time fields
            if "initial" not in kwargs:
                kwargs["initial"] = {}
            kwargs["initial"]["meal_date"] = initial_datetime.date()
            kwargs["initial"]["meal_time"] = initial_datetime.time()
            # Remove the original date_time from initial
            del kwargs["initial"]["date_time"]

        super().__init__(*args, **kwargs)

        # If editing existing meal, populate date and time fields
        if self.instance and self.instance.pk and hasattr(self.instance, "date_time"):
            self.fields["meal_date"].initial = self.instance.date_time.date()
            self.fields["meal_time"].initial = self.instance.date_time.time()

        # Make recipes optional
        self.fields["recipes"].required = False
        # Improve field labels and help text
        self.fields[
            "name"
        ].help_text = "Name your meal (e.g., 'Breakfast', 'Lunch', 'Snack')"
        self.fields["notes"].help_text = "Optional notes about the meal"

    def clean(self) -> dict[str, Any]:
        """Combine date and time fields into datetime field."""
        cleaned_data = super().clean()
        meal_date = cleaned_data.get("meal_date")
        meal_time = cleaned_data.get("meal_time")

        if meal_date and meal_time:
            # Combine date and time into a timezone-aware datetime
            naive_datetime = datetime.combine(meal_date, meal_time)
            cleaned_data["date_time"] = timezone.make_aware(naive_datetime)
        elif meal_date and not meal_time:
            # If only date is provided, default time to current time
            current_time = timezone.now().time()
            naive_datetime = datetime.combine(meal_date, current_time)
            cleaned_data["date_time"] = timezone.make_aware(naive_datetime)
        elif meal_time and not meal_date:
            # If only time is provided, use current date
            current_date = timezone.now().date()
            naive_datetime = datetime.combine(current_date, meal_time)
            cleaned_data["date_time"] = timezone.make_aware(naive_datetime)
        else:
            # If neither is provided, use current datetime
            cleaned_data["date_time"] = timezone.now()

        return cleaned_data

    def save(self, commit: bool = True) -> Meal:
        """Save the meal with the combined datetime."""
        meal: Meal = super().save(commit=False)

        # Set the datetime from cleaned data
        if "date_time" in self.cleaned_data:
            meal.date_time = self.cleaned_data["date_time"]

        if commit:
            meal.save()
            self.save_m2m()

        return meal


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
        import json

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
