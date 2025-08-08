from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import RecipeForm


@login_required
def create_recipe(request: HttpRequest) -> HttpResponse:
    """View for creating a new recipe."""
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("meals:index")  # Redirect to meals index for now
    else:
        form = RecipeForm()

    return render(
        request, "recipes/create_recipe.html", {"form": form, "title": "Add Recipe"}
    )
