"""
Views for the foodmood project.
"""

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """
    Simple index page view showing construction message.
    """
    return render(request, "index.html")


def health_check(request):
    return JsonResponse({"status": "healthy"})
