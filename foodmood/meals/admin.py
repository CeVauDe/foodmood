from django.contrib import admin

from .models import Ingredient, Meal, Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "creation_date"]
    search_fields = ["name", "description"]
    readonly_fields = ["creation_date"]
    ordering = ["name"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "creation_date"]
    search_fields = ["name", "notes"]
    readonly_fields = ["creation_date"]
    inlines = [RecipeIngredientInline]
    ordering = ["name"]


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "date_time", "creation_date"]
    list_filter = ["date_time", "user"]
    search_fields = ["name", "notes", "user__username"]
    readonly_fields = ["creation_date", "update_date"]
    filter_horizontal = ["recipes"]
    ordering = ["-date_time"]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ["recipe", "ingredient", "weight_g"]
    list_filter = ["recipe", "ingredient"]
    search_fields = ["recipe__name", "ingredient__name"]
