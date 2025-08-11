from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from .models import Edible


# Create your views here.
@require_safe
def index(request: HttpRequest) -> HttpResponse:
    latest_edibles = Edible.objects.annotate(
        num_ingedients=Count("ingredients")
    ).order_by("-creation_date")[:10]

    return render(request, "edibles/index.html", context={"edibles": latest_edibles})
