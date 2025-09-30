from django.db import models
from edibles.models import Edible


class Meal(models.Model):
    """
    A meal eaten by the user at a specific time, consisting of one or more edibles.
    """

    class MealCategory(models.TextChoices):
        BREAKFAST = "BREAKFAST", "Breakfast"
        LUNCH = "LUNCH", "Lunch"
        DINNER = "DINNER", "Dinner"
        SNACK = "SNACK", "Snack"

    title: models.CharField = models.CharField(max_length=128, blank=False)
    category: models.CharField = models.CharField(
        max_length=20,
        choices=MealCategory.choices,
        blank=False,
    )
    eaten_at: models.DateTimeField = models.DateTimeField(blank=False)
    edibles: models.ManyToManyField[Edible, Edible] = models.ManyToManyField(
        Edible, related_name="used_in_meals", blank=True
    )
    creation_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    update_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Return a string representation of the meal."""
        formatted_date = self.eaten_at.strftime("%d.%m.%Y %H:%M")
        return f"{self.title} ({self.category}) - {formatted_date}"
