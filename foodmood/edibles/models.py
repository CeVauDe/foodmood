# Create your models here.

from django.db import models


class Edible(models.Model):
    """
    An edible item, that can consist of multiple other edibles, but does not have to
    """

    name: models.CharField = models.CharField(max_length=64)
    creation_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    update_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    ingredients: models.ManyToManyField["Edible", "Edible"] = models.ManyToManyField(
        "Edible", blank=False, related_name="used_in"
    )

    used_in: models.QuerySet["Edible"]

    def __str__(self) -> str:
        return f"{self.name} ({self.ingredients.count()} ingredients)"
