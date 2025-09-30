from django.contrib import admin

from .models import Meal


class MealAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "eaten_at", "creation_date")
    list_filter = ("category", "eaten_at")
    search_fields = ("title",)
    filter_horizontal = ("edibles",)


admin.site.register(Meal, MealAdmin)
