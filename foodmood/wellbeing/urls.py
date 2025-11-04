from django.urls import path

from . import views

app_name = "wellbeing"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    # Categories
    path("categories/", views.category_list, name="category_list"),
    path("categories/create/", views.category_create, name="category_create"),
    path(
        "categories/<int:category_id>/", views.category_detail, name="category_detail"
    ),
    path(
        "categories/<int:category_id>/edit/", views.category_edit, name="category_edit"
    ),
    path(
        "categories/<int:category_id>/toggle/",
        views.category_toggle,
        name="category_toggle",
    ),
    # Options (if managing separately from categories)
    path(
        "categories/<int:category_id>/options/add/",
        views.option_create,
        name="option_create",
    ),
    # Entries
    path("entries/", views.entry_list, name="entry_list"),
    path("entries/create/", views.entry_create, name="entry_create"),
    path("entries/quick/", views.entry_quick, name="entry_quick"),
    path("entries/bulk/", views.entry_bulk, name="entry_bulk"),  # Daily check-in
    path("entries/<int:entry_id>/", views.entry_detail, name="entry_detail"),
    path("entries/<int:entry_id>/edit/", views.entry_edit, name="entry_edit"),
    path("entries/<int:entry_id>/delete/", views.entry_delete, name="entry_delete"),
    # API endpoints for AJAX
    path(
        "api/categories/<int:category_id>/options/",
        views.api_category_options,
        name="api_category_options",
    ),
]
