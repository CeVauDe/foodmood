from django.urls import path

from . import views

app_name = "edibles"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:edible_id>/", views.detail, name="detail"),
    path("api/quick-create/", views.quick_create_edible, name="quick_create"),
]
