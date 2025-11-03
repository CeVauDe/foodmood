# Wellbeing Module - Implementation Plan

## Overview
Add a flexible wellbeing tracking module to the FoodMood app that allows users to define custom categories and log daily wellbeing entries.

---

## Database Design

### Design Pattern: User-Defined Options (Flexible Scale System)

This design allows each category to have its own custom set of response options, making it suitable for:
- Numeric scales (1-10, 1-5)
- Text-based scales (Poor/Fair/Good/Excellent)
- Binary choices (Yes/No, Present/Absent)
- Severity scales (None/Mild/Moderate/Severe)
- Custom options unique to each category

### Model 1: WellbeingCategory
Allows users to define what aspects of wellbeing they want to track.

```python
class WellbeingCategory(models.Model):
    """
    A user-defined category for tracking wellbeing (e.g., Energy, Mood, Sleep Quality, Stress).
    """
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Optional emoji or icon class
    is_active = models.BooleanField(default=True)  # Allow users to archive categories
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.name
```

**Fields:**
- `name`: Category name (e.g., "Mood", "Energy Level", "Sleep Quality")
- `description`: Optional longer description of what this tracks
- `icon`: Optional emoji (😊, ⚡, 😴) or Bootstrap icon class
- `is_active`: Soft delete - hide without removing historical data
- Timestamps for tracking

### Model 2: WellbeingOption
Defines the possible response values for each category.

```python
class WellbeingOption(models.Model):
    """
    A user-defined option for a wellbeing category (e.g., "Excellent", "Good", "Fair", "Poor").
    """
    category = models.ForeignKey(
        WellbeingCategory,
        on_delete=models.CASCADE,
        related_name="options"
    )
    label = models.CharField(max_length=64)  # Display text (e.g., "Excellent", "😊 Happy")
    value = models.IntegerField()  # Numeric value for sorting and analysis (e.g., 1, 2, 3, 4)
    color = models.CharField(max_length=20, blank=True)  # Optional color code (e.g., "success", "warning", "danger")
    order = models.IntegerField(default=0)  # Display order (allows custom sorting)
    
    class Meta:
        ordering = ['order', 'value']
        unique_together = [['category', 'label'], ['category', 'value']]
    
    def __str__(self) -> str:
        return f"{self.category.name}: {self.label}"
```

**Fields:**
- `category`: Foreign key to WellbeingCategory
- `label`: Display text shown to user (e.g., "Excellent", "5/10", "😊 Happy")
- `value`: Numeric value for sorting, graphing, and calculations (allows text labels with numeric analysis)
- `color`: Optional Bootstrap color class (primary, success, warning, danger) for visual feedback
- `order`: Custom display order (in case logical order differs from value order)

**Design Rationale:**
- Separates "what user sees" (label) from "what we analyze" (value)
- Allows emojis, text, or numbers in labels while maintaining numeric values
- Color coding provides instant visual feedback
- Unique together constraint prevents duplicate labels/values per category

### Model 3: WellbeingEntry
Individual wellbeing log entries.

```python
class WellbeingEntry(models.Model):
    """
    A single wellbeing entry for a specific category at a specific time.
    """
    category = models.ForeignKey(
        WellbeingCategory, 
        on_delete=models.CASCADE,
        related_name="entries"
    )
    option = models.ForeignKey(
        WellbeingOption,
        on_delete=models.PROTECT,  # Don't allow deleting options that have been used
        related_name="entries"
    )
    notes = models.TextField(blank=True)  # Optional free-text notes
    recorded_at = models.DateTimeField()  # When this wellbeing state occurred
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['recorded_at']),
            models.Index(fields=['category', 'recorded_at']),
        ]
        ordering = ['-recorded_at']
        verbose_name_plural = "Wellbeing entries"
    
    def __str__(self) -> str:
        return f"{self.category.name}: {self.option.label} at {self.recorded_at}"
```

**Fields:**
- `category`: Foreign key to WellbeingCategory (for quick filtering)
- `option`: Foreign key to WellbeingOption (the actual response)
- `notes`: Optional text for context or details
- `recorded_at`: When the user felt this way (vs. when they logged it)
- Timestamps for tracking

**Design Rationale:**
- Category FK allows filtering without joining through options
- PROTECT on option prevents accidental deletion of historical data
- Related name `entries` allows `option.entries.all()` and `category.entries.all()` queries
- Can still do numeric analysis using `option.value`

---

## Example Data Structures

### Example 1: Mood Category with Text Labels
```python
category = WellbeingCategory(name="Mood", icon="😊")

options = [
    WellbeingOption(category=category, label="😫 Terrible", value=1, color="danger", order=1),
    WellbeingOption(category=category, label="😔 Poor", value=2, color="danger", order=2),
    WellbeingOption(category=category, label="😐 Okay", value=3, color="warning", order=3),
    WellbeingOption(category=category, label="🙂 Good", value=4, color="success", order=4),
    WellbeingOption(category=category, label="😄 Excellent", value=5, color="success", order=5),
]
```

### Example 2: Pain Level with Severity Scale
```python
category = WellbeingCategory(name="Pain Level", icon="🩹")

options = [
    WellbeingOption(category=category, label="None", value=0, color="success", order=1),
    WellbeingOption(category=category, label="Mild", value=1, color="info", order=2),
    WellbeingOption(category=category, label="Moderate", value=2, color="warning", order=3),
    WellbeingOption(category=category, label="Severe", value=3, color="danger", order=4),
]
```

### Example 3: Binary Yes/No
```python
category = WellbeingCategory(name="Exercised Today", icon="🏃")

options = [
    WellbeingOption(category=category, label="No", value=0, color="secondary", order=1),
    WellbeingOption(category=category, label="Yes", value=1, color="success", order=2),
]
```

### Example 4: Traditional 1-10 Scale
```python
category = WellbeingCategory(name="Energy Level", icon="⚡")

options = [
    WellbeingOption(category=category, label=str(i), value=i, order=i)
    for i in range(1, 11)
]
# Add color coding
options[0:3].color = "danger"  # 1-3: red
options[3:7].color = "warning"  # 4-7: yellow
options[7:10].color = "success"  # 8-10: green
```

---

## Comparison: Numeric Scale vs User-Defined Options

| Aspect | Numeric Scale (Original) | User-Defined Options |
|--------|-------------------------|---------------------|
| **Simplicity** | ✅ Simpler (2 models) | ⚠️ More complex (3 models) |
| **Flexibility** | ⚠️ Limited to 1-10 | ✅ Unlimited flexibility |
| **Setup Required** | ✅ None | ⚠️ Must define options per category |
| **Query Complexity** | ✅ Simple (direct value) | ⚠️ Requires join through options |
| **Analysis** | ✅ Direct numeric | ✅ Numeric via option.value |
| **User Experience** | ⚠️ Always sees numbers | ✅ Meaningful labels |
| **Validation** | ✅ Simple range check | ✅ FK constraint |
| **Yes/No Questions** | ❌ Awkward (use 1 & 10?) | ✅ Natural |
| **Severity Scales** | ❌ Requires documentation | ✅ Self-documenting |
| **Customization** | ❌ Fixed scale | ✅ Per-category scales |

---

## Alternative Design Considerations

### Option A: Single Entry, Multiple Categories with Numeric Scale (Original)
**Pros:** Simple, flexible, easy to query by category, easy to graph
**Cons:** More database rows if tracking multiple categories daily, limited to numeric values

### Option B: Single Entry, JSON for Multiple Categories
```python
class WellbeingEntry(models.Model):
    recorded_at = models.DateTimeField()
    values = models.JSONField()  # {"mood": 8, "energy": 6, "sleep": 7}
    notes = models.TextField(blank=True)
```
**Pros:** One row per day/time period
**Cons:** Harder to query, less flexible, no foreign key validation

### Option C: Predefined Categories with Choices
**Pros:** Simpler for fixed set of categories
**Cons:** Not user-customizable, requires code changes to add categories

### Option D: User-Defined Options (Enum-Like) 🌟 RECOMMENDED
**Pros:** Maximum flexibility, supports any type of scale (numeric, text, yes/no, severity levels)
**Cons:** More complex database structure, requires additional model

**Recommendation:** Use Option D (user-defined options) for true flexibility across all use cases.

---

## Features to Implement

### Phase 1: Core Functionality
1. **Category Management**
   - List all categories
   - Create new category
   - Edit category (name, description, icon)
   - Archive/unarchive category (soft delete)

2. **Entry Logging**
   - Form to create new entry
   - Select category, rate 1-10, add optional notes
   - Default `recorded_at` to now, allow editing
   - Quick entry form (minimal fields)

3. **Entry List/History**
   - View all entries (paginated)
   - Filter by category
   - Filter by date range
   - Edit existing entries
   - Delete entries

### Phase 2: Enhanced Features
4. **Dashboard/Summary View**
   - Today's entries at a glance
   - Average scores by category (last 7/30 days)
   - Simple trend indicators (↑↓→)

5. **Bulk Entry Creation**
   - Create entries for multiple categories at once
   - "Daily Check-in" form with all active categories

6. **Data Visualization**
   - Line charts showing trends over time
   - Comparison between categories
   - Correlation with meals (future integration)

### Phase 3: Advanced Features
7. **Reminders & Notifications**
   - Remind user to log entries daily
   - Configurable reminder times

8. **Export & Reports**
   - Export data as CSV/JSON
   - Weekly/monthly summary reports

9. **Integration with Other Modules**
   - Correlate wellbeing with meals eaten
   - Identify food mood patterns

---

## File Structure

```
foodmood/
  wellbeing/
    __init__.py
    admin.py                 # Register models for admin interface
    apps.py                  # App configuration
    models.py                # WellbeingCategory, WellbeingEntry
    forms.py                 # CategoryForm, EntryForm, QuickEntryForm
    views.py                 # List, create, edit, delete views
    urls.py                  # URL routing
    tests.py                 # Unit tests
    migrations/
      __init__.py
      0001_initial.py
    templates/
      wellbeing/
        category_list.html    # List all categories
        category_form.html    # Create/edit category
        entry_list.html       # List entries with filters
        entry_form.html       # Create/edit entry
        entry_quick.html      # Quick entry form
        dashboard.html        # Summary/overview (Phase 2)
```

---

## URL Structure

```python
# wellbeing/urls.py
app_name = "wellbeing"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    
    # Categories
    path("categories/", views.category_list, name="category_list"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/<int:category_id>/", views.category_detail, name="category_detail"),
    path("categories/<int:category_id>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:category_id>/toggle/", views.category_toggle, name="category_toggle"),
    
    # Options (if managing separately from categories)
    path("categories/<int:category_id>/options/add/", views.option_create, name="option_create"),
    
    # Entries
    path("entries/", views.entry_list, name="entry_list"),
    path("entries/create/", views.entry_create, name="entry_create"),
    path("entries/quick/", views.entry_quick, name="entry_quick"),
    path("entries/bulk/", views.entry_bulk, name="entry_bulk"),  # Daily check-in
    path("entries/<int:entry_id>/", views.entry_detail, name="entry_detail"),
    path("entries/<int:entry_id>/edit/", views.entry_edit, name="entry_edit"),
    path("entries/<int:entry_id>/delete/", views.entry_delete, name="entry_delete"),
    
    # API endpoints for AJAX
    path("api/categories/<int:category_id>/options/", views.api_category_options, name="api_category_options"),
]
```

Add to main `foodmood/urls.py`:
```python
path("wellbeing/", include("wellbeing.urls")),
```

---

## Forms

### CategoryForm
```python
class CategoryForm(forms.ModelForm):
    class Meta:
        model = WellbeingCategory
        fields = ['name', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '😊'}),
        }
```

### OptionForm
```python
class OptionForm(forms.ModelForm):
    """Form for creating/editing individual options for a category."""
    class Meta:
        model = WellbeingOption
        fields = ['label', 'value', 'color', 'order']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Excellent, 😊 Happy'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Numeric value for analysis'}),
            'color': forms.Select(
                choices=[
                    ('', 'Default'),
                    ('primary', 'Blue'),
                    ('secondary', 'Gray'),
                    ('success', 'Green'),
                    ('info', 'Cyan'),
                    ('warning', 'Yellow'),
                    ('danger', 'Red'),
                ],
                attrs={'class': 'form-select'}
            ),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
```

### OptionFormSet
```python
from django.forms import inlineformset_factory

OptionFormSet = inlineformset_factory(
    WellbeingCategory,
    WellbeingOption,
    form=OptionForm,
    extra=3,  # Show 3 empty forms by default
    can_delete=True,
    min_num=2,  # Require at least 2 options
    validate_min=True,
)
```

### EntryForm (Full)
```python
class EntryForm(forms.ModelForm):
    """Full entry form with all fields."""
    class Meta:
        model = WellbeingEntry
        fields = ['category', 'option', 'recorded_at', 'notes']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'option': forms.Select(attrs={'class': 'form-select'}),
            'recorded_at': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If category is pre-selected, filter options
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['option'].queryset = WellbeingOption.objects.filter(
                    category_id=category_id
                ).order_by('order', 'value')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['option'].queryset = self.instance.category.options.all()
```

### QuickEntryForm (Minimal)
```python
class QuickEntryForm(forms.ModelForm):
    """Quick entry form for fast logging."""
    class Meta:
        model = WellbeingEntry
        fields = ['category', 'option']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'option': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Auto-set recorded_at to now in view
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['option'].queryset = WellbeingOption.objects.filter(
                    category_id=category_id
                ).order_by('order', 'value')
            except (ValueError, TypeError):
                pass

class BulkEntryForm(forms.Form):
    """Form for logging multiple categories at once (daily check-in)."""
    recorded_at = forms.DateTimeField(
        initial=timezone.now,
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add a field for each active category
        categories = WellbeingCategory.objects.filter(is_active=True).prefetch_related('options')
        for category in categories:
            field_name = f'category_{category.id}'
            self.fields[field_name] = forms.ModelChoiceField(
                queryset=category.options.all(),
                required=False,
                label=f"{category.icon} {category.name}" if category.icon else category.name,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                empty_label="Skip"
            )
```

---

## Views Strategy

Follow the pattern from `edibles` and `meals` modules:

1. **Function-based views** with `@require_http_methods` decorators
2. **Type hints** for request and response
3. **Bootstrap 5** styled templates extending `layout.html`
4. **Consistent naming**: `list`, `detail`, `create`, `edit`, `delete`

### Key View Examples

#### Category Create/Edit with Options
```python
from django.db import transaction

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
    
    return render(request, "wellbeing/category_form.html", {
        "form": form,
        "formset": formset,
        "action": "Create"
    })

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
    
    return render(request, "wellbeing/category_form.html", {
        "form": form,
        "formset": formset,
        "category": category,
        "action": "Edit"
    })
```

#### Entry Create with Dynamic Option Loading
```python
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
        category_id = request.GET.get('category')
        initial = {'recorded_at': timezone.now()}
        if category_id:
            initial['category'] = category_id
        form = EntryForm(initial=initial)
    
    return render(request, "wellbeing/entry_form.html", {
        "form": form,
        "categories": WellbeingCategory.objects.filter(is_active=True).prefetch_related('options')
    })
```

#### Quick Entry with AJAX
```python
@require_http_methods(["GET", "POST"])
def entry_quick(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = QuickEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.recorded_at = timezone.now()
            entry.save()
            
            # Return JSON for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'ok': True,
                    'entry_id': entry.id,
                    'category': entry.category.name,
                    'option': entry.option.label
                })
            return redirect("wellbeing:dashboard")
    else:
        form = QuickEntryForm()
    
    return render(request, "wellbeing/entry_quick.html", {"form": form})

@require_http_methods(["GET"])
def api_category_options(request: HttpRequest, category_id: int) -> JsonResponse:
    """API endpoint to get options for a category (for dynamic form updates)."""
    options = WellbeingOption.objects.filter(
        category_id=category_id
    ).order_by('order', 'value').values('id', 'label', 'value', 'color')
    
    return JsonResponse({'options': list(options)})
```

#### Bulk Entry (Daily Check-in)
```python
@require_http_methods(["GET", "POST"])
def entry_bulk(request: HttpRequest) -> HttpResponse:
    """Create entries for multiple categories at once."""
    if request.method == "POST":
        form = BulkEntryForm(request.POST)
        if form.is_valid():
            recorded_at = form.cleaned_data['recorded_at']
            notes = form.cleaned_data.get('notes', '')
            
            entries_created = 0
            with transaction.atomic():
                for field_name, option in form.cleaned_data.items():
                    if field_name.startswith('category_') and option:
                        category_id = int(field_name.split('_')[1])
                        category = WellbeingCategory.objects.get(pk=category_id)
                        WellbeingEntry.objects.create(
                            category=category,
                            option=option,
                            recorded_at=recorded_at,
                            notes=notes
                        )
                        entries_created += 1
            
            messages.success(request, f"Created {entries_created} wellbeing entries")
            return redirect("wellbeing:dashboard")
    else:
        form = BulkEntryForm()
    
    return render(request, "wellbeing/entry_bulk.html", {"form": form})
```

---

## Admin Interface

Register all models for easy backend management:

```python
# wellbeing/admin.py
from django.contrib import admin
from .models import WellbeingCategory, WellbeingOption, WellbeingEntry

class WellbeingOptionInline(admin.TabularInline):
    """Inline admin for options within category."""
    model = WellbeingOption
    extra = 1
    fields = ['label', 'value', 'color', 'order']
    ordering = ['order', 'value']

@admin.register(WellbeingCategory)
class WellbeingCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'option_count', 'is_active', 'creation_date']
    list_filter = ['is_active', 'creation_date']
    search_fields = ['name', 'description']
    inlines = [WellbeingOptionInline]
    
    def option_count(self, obj):
        return obj.options.count()
    option_count.short_description = 'Options'

@admin.register(WellbeingOption)
class WellbeingOptionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'category', 'value', 'color', 'order']
    list_filter = ['category', 'color']
    search_fields = ['label', 'category__name']
    ordering = ['category', 'order', 'value']

@admin.register(WellbeingEntry)
class WellbeingEntryAdmin(admin.ModelAdmin):
    list_display = ['category', 'option', 'option_value', 'recorded_at', 'creation_date']
    list_filter = ['category', 'recorded_at', 'creation_date']
    search_fields = ['notes', 'category__name', 'option__label']
    date_hierarchy = 'recorded_at'
    autocomplete_fields = ['option']  # Easier selection for categories with many options
    
    def option_value(self, obj):
        return obj.option.value
    option_value.short_description = 'Value'
```

---

## Templates

### Category Form with Inline Option Management
```html
{% extends "layout.html" %}

{% block title %}{{ action }} Category{% endblock %}

{% block body %}
<div class="main-container">
    <h1>{{ action }} Wellbeing Category</h1>
    
    <form method="post">
        {% csrf_token %}
        
        <div class="card mb-3">
            <div class="card-header">
                <h5>Category Details</h5>
            </div>
            <div class="card-body">
                {{ form.as_p }}
            </div>
        </div>
        
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5>Response Options</h5>
                <small class="text-muted">Define the possible values for this category</small>
            </div>
            <div class="card-body">
                {{ formset.management_form }}
                <table class="table">
                    <thead>
                        <tr>
                            <th>Label</th>
                            <th>Value</th>
                            <th>Color</th>
                            <th>Order</th>
                            <th>Delete</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for form in formset %}
                        <tr>
                            <td>{{ form.label }}</td>
                            <td>{{ form.value }}</td>
                            <td>{{ form.color }}</td>
                            <td>{{ form.order }}</td>
                            <td>{{ form.DELETE }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <small class="text-muted">
                    💡 Tip: Use emojis in labels (😊 😔 😴), set values for sorting/analysis, and choose colors for visual feedback.
                </small>
            </div>
        </div>
        
        <button type="submit" class="btn btn-primary">Save Category</button>
        <a href="{% url 'wellbeing:category_list' %}" class="btn btn-secondary">Cancel</a>
    </form>
</div>
{% endblock %}
```

### Entry Quick Form with Visual Options
```html
{% extends "layout.html" %}

{% block title %}Quick Entry{% endblock %}

{% block body %}
<div class="main-container">
    <h1>Quick Wellbeing Entry</h1>
    
    <form method="post" id="quick-entry-form">
        {% csrf_token %}
        
        <div class="mb-3">
            <label for="{{ form.category.id_for_label }}" class="form-label">What are you tracking?</label>
            {{ form.category }}
        </div>
        
        <div class="mb-3" id="options-container" style="display:none;">
            <label class="form-label">How do you feel?</label>
            <div id="options-list" class="d-flex flex-wrap gap-2">
                <!-- Options will be loaded dynamically -->
            </div>
        </div>
        
        <button type="submit" class="btn btn-primary" disabled id="submit-btn">Log Entry</button>
    </form>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('{{ form.category.id_for_label }}');
    const optionsContainer = document.getElementById('options-container');
    const optionsList = document.getElementById('options-list');
    const submitBtn = document.getElementById('submit-btn');
    
    categorySelect.addEventListener('change', function() {
        const categoryId = this.value;
        if (!categoryId) {
            optionsContainer.style.display = 'none';
            return;
        }
        
        // Fetch options for selected category
        fetch(`/wellbeing/api/categories/${categoryId}/options/`)
            .then(response => response.json())
            .then(data => {
                optionsList.innerHTML = '';
                data.options.forEach(option => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = `btn btn-${option.color || 'outline-primary'} option-btn`;
                    btn.dataset.optionId = option.id;
                    btn.textContent = option.label;
                    btn.addEventListener('click', function() {
                        // Remove active class from all buttons
                        document.querySelectorAll('.option-btn').forEach(b => {
                            b.classList.remove('active');
                        });
                        // Add active class to clicked button
                        this.classList.add('active');
                        // Create hidden input for selected option
                        let input = document.getElementById('selected-option');
                        if (!input) {
                            input = document.createElement('input');
                            input.type = 'hidden';
                            input.name = 'option';
                            input.id = 'selected-option';
                            document.getElementById('quick-entry-form').appendChild(input);
                        }
                        input.value = option.id;
                        submitBtn.disabled = false;
                    });
                    optionsList.appendChild(btn);
                });
                optionsContainer.style.display = 'block';
            });
    });
});
</script>
{% endblock %}
```

### Dashboard/Entry List Layout
```html
{% extends "layout.html" %}

{% block title %}Wellbeing Tracker{% endblock %}

{% block body %}
<div class="main-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Wellbeing Tracker</h1>
        <div>
            <a href="{% url 'wellbeing:entry_quick' %}" class="btn btn-primary">
                Quick Entry
            </a>
            <a href="{% url 'wellbeing:entry_bulk' %}" class="btn btn-info">
                Daily Check-in
            </a>
            <a href="{% url 'wellbeing:category_list' %}" class="btn btn-outline-secondary">
                Manage Categories
            </a>
        </div>
    </div>

    <!-- Recent entries -->
    <div class="table-responsive">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Value</th>
                    <th>When</th>
                    <th>Notes</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for entry in entries %}
                <tr>
                    <td>
                        {% if entry.category.icon %}{{ entry.category.icon }}{% endif %}
                        {{ entry.category.name }}
                    </td>
                    <td>
                        <span class="badge bg-{{ entry.option.color|default:'secondary' }}">
                            {{ entry.option.label }}
                        </span>
                        <small class="text-muted">({{ entry.option.value }})</small>
                    </td>
                    <td>{{ entry.recorded_at|date:"d.m.Y H:i" }}</td>
                    <td>{{ entry.notes|truncatewords:10 }}</td>
                    <td>
                        <a href="{% url 'wellbeing:entry_edit' entry.id %}" class="btn btn-sm btn-outline-primary">Edit</a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="5" class="text-center">No entries yet. Start tracking your wellbeing!</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

---

## Implementation Steps

### Step 1: Create App Structure
```bash
cd foodmood
python manage.py startapp wellbeing
```

### Step 2: Add to INSTALLED_APPS
In `foodmood/settings.py`:
```python
INSTALLED_APPS = [
    # ... existing apps ...
    "wellbeing",
]
```

### Step 3: Create Models
Implement `WellbeingCategory` and `WellbeingEntry` in `models.py`

### Step 4: Create and Run Migrations
```bash
python manage.py makemigrations wellbeing
python manage.py migrate
```

### Step 5: Register in Admin
Set up `admin.py` for easy testing

### Step 6: Create Forms
Implement forms in `forms.py`

### Step 7: Create Views
Start with basic list and create views

### Step 8: Set Up URLs
Create `urls.py` and add to main URLs

### Step 9: Create Templates
Build templates following Bootstrap 5 styling

### Step 10: Test
Create entries, verify functionality

---

## Testing Strategy

### Unit Tests
```python
# wellbeing/tests.py
from django.test import TestCase
from django.utils import timezone
from .models import WellbeingCategory, WellbeingOption, WellbeingEntry

class WellbeingCategoryTestCase(TestCase):
    def test_create_category(self):
        category = WellbeingCategory.objects.create(name="Mood", icon="😊")
        self.assertEqual(category.name, "Mood")
        self.assertTrue(category.is_active)
    
    def test_category_with_options(self):
        category = WellbeingCategory.objects.create(name="Energy")
        WellbeingOption.objects.create(category=category, label="Low", value=1)
        WellbeingOption.objects.create(category=category, label="High", value=10)
        
        self.assertEqual(category.options.count(), 2)

class WellbeingOptionTestCase(TestCase):
    def setUp(self):
        self.category = WellbeingCategory.objects.create(name="Pain Level")
    
    def test_create_option(self):
        option = WellbeingOption.objects.create(
            category=self.category,
            label="Mild",
            value=1,
            color="warning"
        )
        self.assertEqual(option.label, "Mild")
        self.assertEqual(option.category, self.category)
    
    def test_option_ordering(self):
        opt1 = WellbeingOption.objects.create(category=self.category, label="High", value=3, order=2)
        opt2 = WellbeingOption.objects.create(category=self.category, label="Low", value=1, order=1)
        opt3 = WellbeingOption.objects.create(category=self.category, label="Medium", value=2, order=3)
        
        options = list(self.category.options.all())
        self.assertEqual(options[0], opt2)  # order=1
        self.assertEqual(options[1], opt1)  # order=2
        self.assertEqual(options[2], opt3)  # order=3
    
    def test_unique_constraint(self):
        WellbeingOption.objects.create(category=self.category, label="None", value=0)
        
        # Should not allow duplicate label in same category
        with self.assertRaises(Exception):
            WellbeingOption.objects.create(category=self.category, label="None", value=1)

class WellbeingEntryTestCase(TestCase):
    def setUp(self):
        self.category = WellbeingCategory.objects.create(name="Mood")
        self.option_good = WellbeingOption.objects.create(
            category=self.category,
            label="Good",
            value=8
        )
        self.option_poor = WellbeingOption.objects.create(
            category=self.category,
            label="Poor",
            value=3
        )
    
    def test_create_entry(self):
        entry = WellbeingEntry.objects.create(
            category=self.category,
            option=self.option_good,
            recorded_at=timezone.now()
        )
        self.assertEqual(entry.option.label, "Good")
        self.assertEqual(entry.category.name, "Mood")
    
    def test_entry_with_notes(self):
        entry = WellbeingEntry.objects.create(
            category=self.category,
            option=self.option_poor,
            recorded_at=timezone.now(),
            notes="Felt tired all day"
        )
        self.assertIn("tired", entry.notes)
    
    def test_option_protect_on_delete(self):
        """Options with entries should be protected from deletion."""
        entry = WellbeingEntry.objects.create(
            category=self.category,
            option=self.option_good,
            recorded_at=timezone.now()
        )
        
        # Should raise ProtectedError when trying to delete option
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            self.option_good.delete()
```

### Integration Tests
```python
class WellbeingViewsTestCase(TestCase):
    def test_category_list_view(self):
        response = self.client.get('/wellbeing/categories/')
        self.assertEqual(response.status_code, 200)
    
    def test_entry_create_view(self):
        category = WellbeingCategory.objects.create(name="Energy")
        option = WellbeingOption.objects.create(category=category, label="High", value=10)
        
        response = self.client.post('/wellbeing/entries/create/', {
            'category': category.id,
            'option': option.id,
            'recorded_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertEqual(WellbeingEntry.objects.count(), 1)
```

---

## UI/UX Considerations

1. **Quick Entry Focus**: Make daily logging as frictionless as possible
2. **Visual Feedback**: Use color coding for values (red=low, yellow=mid, green=high)
3. **Mobile-Friendly**: Responsive design for on-the-go logging
4. **Icons**: Use emojis for visual category identification
5. **Validation**: Ensure value is 1-10, required fields are filled

---

## Future Enhancements

1. **Custom Scales**: Allow categories to define their own scale (1-5, 1-10, 0-100)
2. **Tags**: Add tags to entries for additional categorization
3. **Photos**: Attach photos to entries
4. **Templates**: Pre-defined category sets (Mental Health, Physical Health, etc.)
5. **API**: REST API for mobile app integration
6. **Analytics**: Machine learning to identify patterns
7. **Social**: Share anonymous trends with community

---

## Security Considerations

1. **User Authentication**: Add user field to models when auth is implemented
2. **Authorization**: Ensure users can only see/edit their own data
3. **Validation**: Sanitize text inputs to prevent XSS
4. **Rate Limiting**: Prevent spam entries

---

## Database Considerations

### Indexes
Add indexes for common queries:
```python
class WellbeingEntry(models.Model):
    # ... fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['recorded_at']),
            models.Index(fields=['category', 'recorded_at']),
        ]
        ordering = ['-recorded_at']
```

### Performance
- Use `select_related('category')` when querying entries
- Paginate entry lists
- Consider aggregation for dashboard stats

---

## Sample Data

### Suggested Categories
- **Mood** 😊 - Overall emotional state
- **Energy** ⚡ - Physical energy level
- **Sleep Quality** 😴 - How well you slept
- **Stress** 😰 - Stress/anxiety level
- **Focus** 🎯 - Ability to concentrate
- **Social** 👥 - Social connection/interaction
- **Physical Activity** 🏃 - Exercise level
- **Motivation** 💪 - Drive and motivation

### Value Scale Interpretation
- **1-3**: Low/Poor/Negative
- **4-6**: Medium/Moderate/Neutral
- **7-10**: High/Good/Positive

---

## Integration Points

### With Meals Module
Track correlation between:
- What you eat (meals) → How you feel (wellbeing)
- Meal timing → Energy/mood patterns
- Specific ingredients → Wellbeing categories

Future query examples:
```python
# Average mood when eating breakfast
meals_with_breakfast = Meal.objects.filter(category='BREAKFAST')
# Join with wellbeing entries from same day
```

### With Users Module
- Associate all data with specific users
- User preferences for categories
- Privacy settings

---

## Key Differences: User-Defined Options vs Fixed Numeric Scale

### Database Complexity
- **Numeric Scale**: 2 models (Category, Entry)
- **User-Defined Options**: 3 models (Category, Option, Entry)

### Setup Workflow
**Numeric Scale:**
1. Create category → Start logging immediately

**User-Defined Options:**
1. Create category
2. Define options for category
3. Start logging

### Query Examples

**Numeric Scale:**
```python
# Get all high-energy entries (>7)
entries = WellbeingEntry.objects.filter(category__name="Energy", value__gt=7)

# Average mood this week
avg = WellbeingEntry.objects.filter(
    category__name="Mood",
    recorded_at__gte=week_ago
).aggregate(Avg('value'))
```

**User-Defined Options:**
```python
# Get all high-energy entries
entries = WellbeingEntry.objects.filter(
    category__name="Energy",
    option__value__gt=7
)

# Average mood this week
avg = WellbeingEntry.objects.filter(
    category__name="Mood",
    recorded_at__gte=week_ago
).aggregate(Avg('option__value'))

# Additional capability: Filter by specific label
happy_entries = WellbeingEntry.objects.filter(
    category__name="Mood",
    option__label__icontains="happy"
)
```

### When to Use Each Approach

**Use Numeric Scale (1-10) if:**
- ✅ All categories can be represented on a numeric scale
- ✅ You want minimal setup and maximum simplicity
- ✅ Users understand numeric ratings intuitively
- ✅ You don't need Yes/No or severity-based categories

**Use User-Defined Options if:**
- ✅ You need flexibility for different types of scales
- ✅ You want self-documenting labels (users see "Excellent" not "8")
- ✅ You have binary (Yes/No) or categorical data
- ✅ You want visual color coding per option
- ✅ Different categories need different scales (1-5 vs 1-10 vs text)
- ✅ You want users to customize their own response options

### Hybrid Approach (Best of Both Worlds)

You could also implement a hybrid where:
- Categories can choose between "numeric scale" or "custom options"
- A `scale_type` field on `WellbeingCategory` determines which to use
- Numeric scale categories skip the options table
- Custom categories use the options table

```python
class WellbeingCategory(models.Model):
    SCALE_NUMERIC = 'NUMERIC'
    SCALE_CUSTOM = 'CUSTOM'
    SCALE_CHOICES = [
        (SCALE_NUMERIC, 'Numeric Scale (1-10)'),
        (SCALE_CUSTOM, 'Custom Options'),
    ]
    
    scale_type = models.CharField(max_length=10, choices=SCALE_CHOICES, default=SCALE_NUMERIC)
    # ... other fields
```

This adds complexity but provides maximum flexibility.

---

## Migration Path

If you start with the numeric scale and later want user-defined options:

1. **Create the WellbeingOption model**
2. **Add option FK to WellbeingEntry** (nullable initially)
3. **Data migration**: Create options for existing categories based on their values
4. **Update entries** to reference the appropriate option
5. **Make option FK required**, remove value field

---

## Recommendation

**For your FoodMood app, I recommend the User-Defined Options approach because:**

1. **Better UX**: Labels like "Excellent", "Good", "Fair" are more intuitive than numbers
2. **Flexibility**: Supports Yes/No tracking (e.g., "Did I exercise today?")
3. **Visual Feedback**: Color-coded options provide instant visual cues
4. **Future-Proof**: Easy to add new category types without schema changes
5. **Self-Documenting**: Historical data shows meaningful labels, not just numbers
6. **Consistency**: Matches your edibles/meals pattern of using related models

The added complexity is worth it for the flexibility and better user experience.

---

## Summary

The wellbeing module with user-defined options provides a flexible, user-customizable tracking system that:
- ✅ Supports any type of scale or response format
- ✅ Provides meaningful, self-documenting labels
- ✅ Allows visual color coding for instant feedback
- ✅ Follows existing project patterns
- ✅ Provides room for future enhancements
- ✅ Integrates naturally with existing modules
- ✅ Maintains numeric values for analysis while showing friendly labels

Start with Phase 1 (core functionality with category and option management), then expand based on usage and feedback.
