from django.urls import path

from . import views

app_name = "meals"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:meal_id>/", views.detail, name="detail"),
]
