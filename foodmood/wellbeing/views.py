from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import (
    BulkEntryForm,
    CategoryForm,
    EntryForm,
    OptionFormSet,
    QuickEntryForm,
)
from .models import WellbeingCategory, WellbeingEntry, WellbeingOption


@require_http_methods(["GET"])
def dashboard(request: HttpRequest) -> HttpResponse:
    """Main wellbeing dashboard showing recent entries."""
    entries = WellbeingEntry.objects.select_related("category", "option").order_by(
        "-recorded_at"
    )[:20]

    return render(
        request,
        "wellbeing/index.html",
        {
            "entries": entries,
        },
    )


@require_http_methods(["GET"])
def category_list(request: HttpRequest) -> HttpResponse:
    """List all wellbeing categories."""
    categories = WellbeingCategory.objects.prefetch_related("options").order_by("name")

    return render(
        request,
        "wellbeing/category_list.html",
        {
            "categories": categories,
        },
    )


@require_http_methods(["GET"])
def category_detail(request: HttpRequest, category_id: int) -> HttpResponse:
    """View details of a specific category."""
    category = get_object_or_404(
        WellbeingCategory.objects.prefetch_related("options"), pk=category_id
    )
    recent_entries = category.entries.select_related("option")[:10]

    return render(
        request,
        "wellbeing/category_detail.html",
        {
            "category": category,
            "recent_entries": recent_entries,
        },
    )


@require_http_methods(["POST"])
def category_toggle(request: HttpRequest, category_id: int) -> HttpResponse:
    """Toggle the is_active status of a category."""
    category = get_object_or_404(WellbeingCategory, pk=category_id)
    category.is_active = not category.is_active
    category.save()

    return redirect("wellbeing:category_list")


@require_http_methods(["GET", "POST"])
def option_create(request: HttpRequest, category_id: int) -> HttpResponse:
    """Create a new option for a category."""
    category = get_object_or_404(WellbeingCategory, pk=category_id)

    if request.method == "POST":
        # Simple form handling - in production you'd use a proper form
        label = request.POST.get("label")
        value = request.POST.get("value")
        color = request.POST.get("color", "")
        order = request.POST.get("order", 0)

        if label and value:
            WellbeingOption.objects.create(
                category=category,
                label=label,
                value=int(value),
                color=color,
                order=int(order),
            )
            messages.success(request, f"Added option '{label}' to {category.name}")

        return redirect("wellbeing:category_detail", category_id=category.id)

    return render(
        request,
        "wellbeing/option_form.html",
        {
            "category": category,
        },
    )


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


@require_http_methods(["GET"])
def entry_list(request: HttpRequest) -> HttpResponse:
    """List all entries with optional filtering."""
    entries = WellbeingEntry.objects.select_related("category", "option").order_by(
        "-recorded_at"
    )

    # Filter by category if provided
    category_id = request.GET.get("category")
    if category_id:
        entries = entries.filter(category_id=category_id)

    # Filter by date range if provided
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    if date_from:
        entries = entries.filter(recorded_at__gte=date_from)
    if date_to:
        entries = entries.filter(recorded_at__lte=date_to)

    categories = WellbeingCategory.objects.filter(is_active=True).order_by("name")

    return render(
        request,
        "wellbeing/entry_list.html",
        {
            "entries": entries,
            "categories": categories,
            "selected_category": category_id,
        },
    )


@require_http_methods(["GET"])
def entry_detail(request: HttpRequest, entry_id: int) -> HttpResponse:
    """View details of a specific entry."""
    entry = get_object_or_404(
        WellbeingEntry.objects.select_related("category", "option"), pk=entry_id
    )

    return render(
        request,
        "wellbeing/entry_detail.html",
        {
            "entry": entry,
        },
    )


@require_http_methods(["GET", "POST"])
def entry_edit(request: HttpRequest, entry_id: int) -> HttpResponse:
    """Edit an existing entry."""
    entry = get_object_or_404(WellbeingEntry, pk=entry_id)

    if request.method == "POST":
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Entry updated successfully")
            return redirect("wellbeing:entry_detail", entry_id=entry.id)
    else:
        form = EntryForm(instance=entry)

    return render(
        request,
        "wellbeing/entry_form.html",
        {
            "form": form,
            "entry": entry,
            "action": "Edit",
        },
    )


@require_http_methods(["GET", "POST"])
def entry_delete(request: HttpRequest, entry_id: int) -> HttpResponse:
    """Delete an entry."""
    entry = get_object_or_404(WellbeingEntry, pk=entry_id)

    if request.method == "POST":
        entry.delete()
        messages.success(request, "Entry deleted successfully")
        return redirect("wellbeing:entry_list")

    return render(
        request,
        "wellbeing/entry_delete.html",
        {
            "entry": entry,
        },
    )
