from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import MealForm
from .models import Meal

# Create your views here.


def index(request: HttpRequest) -> HttpResponse:
    """View for the meals index page."""
    context: Dict[str, Any] = {"title": "Meals"}

    if request.user.is_authenticated:
        # Get recent meals for authenticated users
        recent_meals = Meal.objects.filter(user=request.user)[:5]
        context["recent_meals"] = recent_meals

    return render(request, "meals/index.html", context)


@login_required
def create_meal(request: HttpRequest) -> HttpResponse:
    """View for creating a new meal."""
    if request.method == "POST":
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            meal.save()
            form.save_m2m()  # Save many-to-many relationships (recipes)
            return redirect("meals:index")
    else:
        # Pre-populate with current time
        form = MealForm(initial={"date_time": timezone.now()})

    return render(request, "meals/create.html", {"form": form, "title": "Add Meal"})
