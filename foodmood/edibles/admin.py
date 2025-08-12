from django.contrib import admin

from .models import Edible


class EdibleAdmin(admin.ModelAdmin):
    filter_horizontal = ("ingredients",)
    list_display = ("id", "name")


# Register your models here.
admin.site.register(Edible, EdibleAdmin)
