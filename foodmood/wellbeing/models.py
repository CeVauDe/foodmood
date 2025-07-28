from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class WellbeingParameter(models.Model):
    """
    User-configurable parameters that they want to track.
    """

    class ParameterType(models.TextChoices):
        CATEGORIC = "categoric", "Categoric"
        NUMERIC = "numeric", "Numeric"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wellbeing_parameters",
        help_text="User who created this parameter",
    )
    name = models.CharField(
        max_length=200,
        help_text="Name of the parameter (e.g., 'Energy Level', 'Mood', 'Stomach Comfort')",
    )
    type = models.CharField(
        max_length=20,
        choices=ParameterType.choices,
        help_text="Type of the parameter: categoric or numeric",
    )
    options = models.JSONField(
        null=True,
        blank=True,
        help_text="Array of available options (only for categoric parameters)",
    )
    description = models.TextField(
        blank=True, help_text="Optional description of what this parameter tracks"
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure parameter names are unique per user
        unique_together = ["user", "name"]
        # Index for frequent queries
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["type"]),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.name} ({self.type})"

    def clean(self) -> None:
        """
        Validate that categoric parameters have options defined
        """
        if self.type == self.ParameterType.CATEGORIC:
            # Type checking workaround for Django JSONField validation
            if not self.options:
                raise ValidationError(
                    {
                        "options": "Categoric parameters must have at least one option defined as a non-empty list."
                    }
                )
            if not isinstance(self.options, list):  # type: ignore[unreachable]
                raise ValidationError(
                    {
                        "options": "Categoric parameters must have at least one option defined as a non-empty list."
                    }
                )
            if len(self.options) == 0:
                raise ValidationError(
                    {
                        "options": "Categoric parameters must have at least one option defined as a non-empty list."
                    }
                )
        elif self.type == self.ParameterType.NUMERIC:
            # For numeric parameters, options should be None or empty
            if self.options:
                raise ValidationError(
                    {"options": "Numeric parameters should not have options defined."}
                )


class WellbeingEntry(models.Model):
    """
    Actual logged wellbeing data from users.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wellbeing_entries",
        help_text="User who logged this entry",
    )
    parameter = models.ForeignKey(
        WellbeingParameter,
        on_delete=models.CASCADE,
        related_name="entries",
        help_text="The wellbeing parameter this entry is for",
    )
    categoric_value = models.CharField(
        max_length=200,
        blank=True,
        help_text="The value, if it is a categoric parameter",
    )
    numeric_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The value, if it is a numeric parameter",
    )
    date_time = models.DateTimeField(
        default=timezone.now, help_text="When this entry was logged"
    )
    notes = models.TextField(blank=True, help_text="Optional notes about this entry")
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Index for frequent queries
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["parameter"]),
            models.Index(fields=["date_time"]),
            models.Index(
                fields=["user", "date_time"]
            ),  # Composite index for common query pattern
        ]
        ordering = ["-date_time"]  # Most recent first
        verbose_name_plural = "Wellbeing entries"

    def __str__(self) -> str:
        value = self.categoric_value if self.categoric_value else self.numeric_value
        return f"{self.user.username} - {self.parameter.name}: {value} ({self.date_time.strftime('%Y-%m-%d %H:%M')})"

    def clean(self) -> None:
        """
        Validate that entries match their parameter type and constraints
        """
        if not self.parameter:
            raise ValidationError({"parameter": "Parameter must be set."})

        # Ensure user matches between entry and parameter
        if self.parameter.user != self.user:
            raise ValidationError(
                {"parameter": "Parameter must belong to the same user as the entry."}
            )

        if self.parameter.type == WellbeingParameter.ParameterType.CATEGORIC:
            self.clean_catecoric_type()

        elif self.parameter.type == WellbeingParameter.ParameterType.NUMERIC:
            self.clean_numeric_type()

    def clean_catecoric_type(self) -> None:
        # Categoric parameter validation
        if not self.categoric_value:
            raise ValidationError(
                {"categoric_value": "Categoric parameters must have a categoric_value."}
            )
        if self.numeric_value is not None:
            raise ValidationError(
                {
                    "numeric_value": "Categoric parameters should not have a numeric_value."
                }
            )
            # Check if the value is in the allowed options
        options = self.parameter.options
        if options is not None and isinstance(options, list):  # type: ignore[unreachable]
            if self.categoric_value not in options:  # type: ignore[unreachable]
                raise ValidationError(
                    {"categoric_value": f"Value must be one of: {', '.join(options)}"}
                )

    def clean_numeric_type(self) -> None:
        # Numeric parameter validation
        if self.numeric_value is None:
            raise ValidationError(
                {"numeric_value": "Numeric parameters must have a numeric_value."}
            )
        if self.categoric_value:
            raise ValidationError(
                {
                    "categoric_value": "Numeric parameters should not have a categoric_value."
                }
            )
