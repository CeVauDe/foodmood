from django.contrib import admin

from .models import WellbeingCategory, WellbeingEntry, WellbeingOption


class WellbeingOptionInline(admin.TabularInline):
    """Inline admin for options within category."""

    model = WellbeingOption
    extra = 1
    fields = ["label", "value", "color", "order"]
    ordering = ["order", "value"]


@admin.register(WellbeingCategory)
class WellbeingCategoryAdmin(admin.ModelAdmin[WellbeingCategory]):
    list_display = ["name", "icon", "option_count", "is_active", "creation_date"]
    list_filter = ["is_active", "creation_date"]
    search_fields = ["name", "description"]
    inlines = [WellbeingOptionInline]

    @admin.display(description="Options")
    def option_count(self, obj: WellbeingCategory) -> int:
        return obj.options.count()  # type: ignore[attr-defined, no-any-return]


@admin.register(WellbeingOption)
class WellbeingOptionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "category", "value", "color", "order"]
    list_filter = ["category", "color"]
    search_fields = ["label", "category__name"]
    ordering = ["category", "order", "value"]


@admin.register(WellbeingEntry)
class WellbeingEntryAdmin(admin.ModelAdmin[WellbeingEntry]):
    list_display = [
        "category",
        "option",
        "option_value",
        "recorded_at",
        "creation_date",
    ]
    list_filter = ["category", "recorded_at", "creation_date"]
    search_fields = ["notes", "category__name", "option__label"]
    date_hierarchy = "recorded_at"
    autocomplete_fields = [
        "option"
    ]  # Easier selection for categories with many options

    @admin.display(description="Value")
    def option_value(self, obj: WellbeingEntry) -> int:
        return obj.option.value
