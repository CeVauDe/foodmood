from django.urls import path

from . import views

app_name = "meals"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_meal, name="create"),
    path("recipes/create/", views.create_recipe, name="create_recipe"),
]
