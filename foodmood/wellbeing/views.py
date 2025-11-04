from datetime import timezone
from pyexpat.errors import messages

from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from foodmood.wellbeing.forms import (
    BulkEntryForm,
    CategoryForm,
    EntryForm,
    OptionFormSet,
    QuickEntryForm,
)
from foodmood.wellbeing.models import WellbeingCategory, WellbeingEntry, WellbeingOption


@require_http_methods(["GET", "POST"])
def category_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CategoryForm(request.POST)
        formset = OptionFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                category = form.save()
                formset.instance = category
                formset.save()
            return redirect("wellbeing:category_list")
    else:
        form = CategoryForm()
        formset = OptionFormSet()

    return render(
        request,
        "wellbeing/category_form.html",
        {"form": form, "formset": formset, "action": "Create"},
    )


@require_http_methods(["GET", "POST"])
def category_edit(request: HttpRequest, category_id: int) -> HttpResponse:
    category = get_object_or_404(WellbeingCategory, pk=category_id)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        formset = OptionFormSet(request.POST, instance=category)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect("wellbeing:category_detail", category_id=category.id)
    else:
        form = CategoryForm(instance=category)
        formset = OptionFormSet(instance=category)

    return render(
        request,
        "wellbeing/category_form.html",
        {"form": form, "formset": formset, "category": category, "action": "Edit"},
    )


@require_http_methods(["GET", "POST"])
def entry_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            if not entry.recorded_at:
                entry.recorded_at = timezone.now()
            entry.save()
            return redirect("wellbeing:entry_list")
    else:
        # Pre-select category if provided in query params
        category_id = request.GET.get("category")
        initial = {"recorded_at": timezone.now()}
        if category_id:
            initial["category"] = category_id
        form = EntryForm(initial=initial)

    return render(
        request,
        "wellbeing/entry_form.html",
        {
            "form": form,
            "categories": WellbeingCategory.objects.filter(
                is_active=True
            ).prefetch_related("options"),
        },
    )


@require_http_methods(["GET", "POST"])
def entry_quick(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = QuickEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.recorded_at = timezone.now()
            entry.save()

            # Return JSON for AJAX requests
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "ok": True,
                        "entry_id": entry.id,
                        "category": entry.category.name,
                        "option": entry.option.label,
                    }
                )
            return redirect("wellbeing:dashboard")
    else:
        form = QuickEntryForm()

    return render(request, "wellbeing/entry_quick.html", {"form": form})


@require_http_methods(["GET"])
def api_category_options(request: HttpRequest, category_id: int) -> JsonResponse:
    """API endpoint to get options for a category (for dynamic form updates)."""
    options = (
        WellbeingOption.objects.filter(category_id=category_id)
        .order_by("order", "value")
        .values("id", "label", "value", "color")
    )

    return JsonResponse({"options": list(options)})


@require_http_methods(["GET", "POST"])
def entry_bulk(request: HttpRequest) -> HttpResponse:
    """Create entries for multiple categories at once."""
    if request.method == "POST":
        form = BulkEntryForm(request.POST)
        if form.is_valid():
            recorded_at = form.cleaned_data["recorded_at"]
            notes = form.cleaned_data.get("notes", "")

            entries_created = 0
            with transaction.atomic():
                for field_name, option in form.cleaned_data.items():
                    if field_name.startswith("category_") and option:
                        category_id = int(field_name.split("_")[1])
                        category = WellbeingCategory.objects.get(pk=category_id)
                        WellbeingEntry.objects.create(
                            category=category,
                            option=option,
                            recorded_at=recorded_at,
                            notes=notes,
                        )
                        entries_created += 1

            messages.success(request, f"Created {entries_created} wellbeing entries")
            return redirect("wellbeing:dashboard")
    else:
        form = BulkEntryForm()

    return render(request, "wellbeing/entry_bulk.html", {"form": form})
