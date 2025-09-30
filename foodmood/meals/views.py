from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import MealForm
from .models import Meal


@require_http_methods(["GET", "POST"])
def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = MealForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("meals:index")
    else:
        form = MealForm()

    latest_meals = Meal.objects.annotate(num_edibles=Count("edibles")).order_by(
        "-eaten_at"
    )[:10]

    return render(
        request,
        "meals/index.html",
        context={"meals": latest_meals, "form": form},
    )


@require_http_methods(["GET"])
def detail(request: HttpRequest, meal_id: int) -> HttpResponse:
    meal = get_object_or_404(Meal.objects.prefetch_related("edibles"), pk=meal_id)
    return render(
        request,
        "meals/detail.html",
        context={"meal": meal},
    )
