from typing import Any

from django.contrib import admin
from django.http import HttpRequest

from .models import WellbeingEntry, WellbeingParameter


@admin.register(WellbeingParameter)
class WellbeingParameterAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "type", "creation_date"]
    list_filter = ["type", "creation_date", "user"]
    search_fields = ["name", "user__username"]
    readonly_fields = ["creation_date", "update_date"]

    fieldsets = (
        (None, {"fields": ("user", "name", "type", "description")}),
        (
            "Options (for categoric parameters)",
            {
                "fields": ("options",),
                "description": 'Only fill this for categoric parameters. Enter as JSON array, e.g., ["Low", "Medium", "High"]',
            },
        ),
        (
            "Timestamps",
            {"fields": ("creation_date", "update_date"), "classes": ("collapse",)},
        ),
    )


@admin.register(WellbeingEntry)
class WellbeingEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "parameter", "get_value", "date_time", "creation_date"]
    list_filter = ["parameter__type", "date_time", "creation_date", "user", "parameter"]
    search_fields = ["user__username", "parameter__name", "notes"]
    readonly_fields = ["creation_date"]
    date_hierarchy = "date_time"

    fieldsets = (
        (None, {"fields": ("user", "parameter", "date_time")}),
        (
            "Values",
            {
                "fields": ("categoric_value", "numeric_value"),
                "description": "Fill either categoric_value OR numeric_value, depending on parameter type",
            },
        ),
        ("Additional Info", {"fields": ("notes",)}),
        ("Timestamps", {"fields": ("creation_date",), "classes": ("collapse",)}),
    )

    def get_value(self, obj: WellbeingEntry) -> Any:
        """Display the appropriate value based on parameter type"""
        return obj.categoric_value if obj.categoric_value else obj.numeric_value

    # Type ignore for Django admin attribute that mypy doesn't recognize
    get_value.short_description = "Value"  # type: ignore[attr-defined]

    def get_queryset(self, request: HttpRequest) -> Any:
        """Optimize queries by selecting related objects"""
        return super().get_queryset(request).select_related("user", "parameter")
