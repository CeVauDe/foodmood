from django.db import models


class WellbeingCategory(models.Model):
    """
    A user-defined category for tracking wellbeing (e.g., Energy, Mood, Sleep Quality, Stress).
    """

    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Optional emoji or icon class
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class WellbeingOption(models.Model):
    """
    A user-defined option for a wellbeing category (e.g., "Excellent", "Good", "Fair", "Poor").
    """

    category = models.ForeignKey(
        WellbeingCategory, on_delete=models.CASCADE, related_name="options"
    )
    label = models.CharField(
        max_length=64
    )  # Display text (e.g., "Excellent", "😊 Happy")
    value = (
        models.IntegerField()
    )  # Numeric value for sorting and analysis (e.g., 1, 2, 3, 4)
    color = models.CharField(
        max_length=20, blank=True
    )  # Optional color code (e.g., "success", "warning", "danger")
    order = models.IntegerField(default=0)  # Display order (allows custom sorting)

    class Meta:
        ordering = ["order", "value"]
        unique_together = [["category", "label"], ["category", "value"]]

    def __str__(self) -> str:
        return f"{self.category.name}: {self.label}"


class WellbeingEntry(models.Model):
    """
    A single wellbeing entry for a specific category at a specific time.
    """

    category = models.ForeignKey(
        WellbeingCategory, on_delete=models.CASCADE, related_name="entries"
    )
    option = models.ForeignKey(
        WellbeingOption,
        on_delete=models.PROTECT,  # Don't allow deleting options that have been used
        related_name="entries",
    )
    notes = models.TextField(blank=True, max_length=512)
    recorded_at = models.DateTimeField()
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["recorded_at"]),
            models.Index(fields=["category", "recorded_at"]),
        ]
        ordering = ["-recorded_at"]
        verbose_name_plural = "Wellbeing entries"

    def __str__(self) -> str:
        return f"{self.category.name}: {self.option.label} at {self.recorded_at}"
