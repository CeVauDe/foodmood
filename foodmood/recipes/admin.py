from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient


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
    ordering = ["name"]
    inlines = [RecipeIngredientInline]

    def get_queryset(self, request):
        """Optimize queries by prefetching ingredients."""
        qs = super().get_queryset(request)
        return qs.prefetch_related("ingredients")


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ["recipe", "ingredient", "weight_g"]
    list_filter = ["recipe", "ingredient"]
    search_fields = ["recipe__name", "ingredient__name"]
