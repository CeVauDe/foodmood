from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
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


@require_http_methods(["POST"])
def quick_create_edible(request: HttpRequest) -> JsonResponse:
    name = request.POST.get("name", "").strip()
    if not name:
        return JsonResponse({"ok": False, "error": "Name is required"}, status=400)

    # Do not allow duplicates
    existing = Edible.objects.filter(name__iexact=name).first()
    if existing is not None:
        return JsonResponse(
            {"ok": True, "id": existing.pk, "name": existing.name, "existing": True}
        )

    edible = Edible.objects.create(name=name)
    return JsonResponse({"ok": True, "id": edible.pk, "name": edible.name})
