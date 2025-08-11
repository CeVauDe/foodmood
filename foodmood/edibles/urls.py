from django.urls import path

from . import views

app_name = "edibles"

urlpatterns = [
    path("", views.index, name="index"),
]
