from django.contrib.auth.models import User
from django.db import models


class Meal(models.Model):
    """
    The meal model captures when and what the user ate.
    Each meal belongs to a user and can contain multiple recipes.
    """

    name: models.CharField = models.CharField(max_length=200)
    date_time: models.DateTimeField = models.DateTimeField()
    user: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="meals"
    )
    recipes: models.ManyToManyField = models.ManyToManyField(
        "recipes.Recipe", blank=True, related_name="meals"
    )
    notes: models.TextField = models.TextField(blank=True, null=True)
    creation_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    update_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_time"]
        indexes = [
            models.Index(fields=["user", "date_time"]),
            models.Index(fields=["date_time"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self) -> str:
        return f"{str(self.name)} - {str(self.user.username)} ({self.date_time.strftime('%Y-%m-%d %H:%M')})"
