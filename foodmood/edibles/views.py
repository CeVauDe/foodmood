from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import EdibleQuickForm
from .models import Edible


# Create your views here.
@require_http_methods(["GET", "POST"])
def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = EdibleQuickForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("edibles:index")
    else:
        form = EdibleQuickForm()

    latest_edibles = Edible.objects.annotate(
        num_ingedients=Count("ingredients")
    ).order_by("-creation_date")[:10]

    return render(
        request,
        "edibles/index.html",
        context={"edibles": latest_edibles, "form": form},
    )
