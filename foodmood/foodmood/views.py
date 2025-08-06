"""
Views for the foodmood project.
"""

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


def index(request: HttpRequest) -> HttpResponse:
    """
    Simple index page view showing construction message.
    """
    return render(request, "index.html")


@require_http_methods(["GET"])
def health_check(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "healthy"})
