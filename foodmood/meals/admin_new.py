from django.contrib import admin

from .models import Meal


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "date_time", "creation_date"]
    list_filter = ["date_time", "user"]
    search_fields = ["name", "user__username", "notes"]
    readonly_fields = ["creation_date", "update_date"]
    ordering = ["-date_time"]
    filter_horizontal = ["recipes"]

    def get_queryset(self, request):
        """Optimize queries by selecting related objects."""
        qs = super().get_queryset(request)
        return qs.select_related("user").prefetch_related("recipes")
