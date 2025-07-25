"""
Views for the foodmood project.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """
    Simple index page view showing construction message.
    """
    return render(request, "index.html")
