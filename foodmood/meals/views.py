from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request: HttpRequest) -> HttpResponse:
    """View for the meals index page."""
    return render(request, "meals/index.html", {"title": "Meals"})
