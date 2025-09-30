from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from edibles.models import Edible

from .forms import MealForm
from .models import Meal


class MealModelTestCase(TestCase):
    def setUp(self) -> None:
        # Create some edibles for testing
        self.bread = Edible.objects.create(name="Bread")
        self.butter = Edible.objects.create(name="Butter")
        self.apple = Edible.objects.create(name="Apple")

    def test_meal_creation(self) -> None:
        """Test that a meal can be created with all required fields."""
        eaten_at = timezone.make_aware(datetime(2025, 9, 30, 8, 30))
        meal = Meal.objects.create(
            title="Morning Toast",
            category="BREAKFAST",
            eaten_at=eaten_at,
        )
        meal.edibles.set([self.bread, self.butter])

        self.assertEqual(meal.title, "Morning Toast")
        self.assertEqual(meal.category, "BREAKFAST")
        self.assertEqual(meal.eaten_at, eaten_at)
        self.assertEqual(meal.edibles.count(), 2)

    def test_meal_category_choices(self) -> None:
        """Test that meal categories are restricted to valid choices."""
        valid_categories = ["BREAKFAST", "LUNCH", "DINNER", "SNACK"]
        eaten_at = timezone.now()

        for category in valid_categories:
            meal = Meal.objects.create(
                title=f"Test {category}",
                category=category,
                eaten_at=eaten_at,
            )
            self.assertEqual(meal.category, category)

    def test_meal_str_representation(self) -> None:
        """Test the string representation of a meal."""
        eaten_at = timezone.make_aware(datetime(2025, 9, 30, 12, 0))
        meal = Meal.objects.create(
            title="Lunch Salad",
            category="LUNCH",
            eaten_at=eaten_at,
        )
        expected = "Lunch Salad (LUNCH) - 30.09.2025 12:00"
        self.assertEqual(str(meal), expected)

    def test_meal_edibles_relationship(self) -> None:
        """Test the many-to-many relationship with edibles."""
        eaten_at = timezone.now()
        meal = Meal.objects.create(
            title="Snack Time",
            category="SNACK",
            eaten_at=eaten_at,
        )
        meal.edibles.set([self.apple])

        self.assertEqual(meal.edibles.count(), 1)
        self.assertEqual(meal.edibles.first(), self.apple)

    def test_meal_creation_updates_timestamps(self) -> None:
        """Test that creation_date is set automatically."""
        before = timezone.now()
        meal = Meal.objects.create(
            title="Test Meal",
            category="DINNER",
            eaten_at=timezone.now(),
        )
        after = timezone.now()

        self.assertGreaterEqual(meal.creation_date, before)
        self.assertLessEqual(meal.creation_date, after)

    def test_meal_update_timestamp(self) -> None:
        """Test that update_date is updated on save."""
        meal = Meal.objects.create(
            title="Original Title",
            category="BREAKFAST",
            eaten_at=timezone.now(),
        )
        original_update_date = meal.update_date

        # Simulate a small time delay
        meal.title = "Updated Title"
        meal.save()
        meal.refresh_from_db()

        self.assertGreaterEqual(meal.update_date, original_update_date)


class MealFormTestCase(TestCase):
    def setUp(self) -> None:
        self.bread = Edible.objects.create(name="Bread")
        self.jam = Edible.objects.create(name="Jam")

    def test_form_has_all_fields(self) -> None:
        """Test that the form includes all required fields."""
        form = MealForm()
        self.assertIn("title", form.fields)
        self.assertIn("category", form.fields)
        self.assertIn("eaten_at", form.fields)
        self.assertIn("edibles", form.fields)

    def test_form_valid_data(self) -> None:
        """Test form validation with valid data."""
        eaten_at = timezone.now()
        form_data = {
            "title": "Breakfast Toast",
            "category": "BREAKFAST",
            "eaten_at": eaten_at,
            "edibles": [self.bread.pk, self.jam.pk],
        }
        form = MealForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_title(self) -> None:
        """Test form validation fails when title is missing."""
        eaten_at = timezone.now()
        form_data = {
            "category": "LUNCH",
            "eaten_at": eaten_at,
        }
        form = MealForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_missing_category(self) -> None:
        """Test form validation fails when category is missing."""
        eaten_at = timezone.now()
        form_data = {
            "title": "Test Meal",
            "eaten_at": eaten_at,
        }
        form = MealForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_form_missing_eaten_at(self) -> None:
        """Test form validation fails when eaten_at is missing."""
        form_data = {
            "title": "Test Meal",
            "category": "DINNER",
        }
        form = MealForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("eaten_at", form.errors)

    def test_form_edibles_optional(self) -> None:
        """Test that edibles field is optional."""
        eaten_at = timezone.now()
        form_data = {
            "title": "Simple Meal",
            "category": "SNACK",
            "eaten_at": eaten_at,
        }
        form = MealForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_saves_meal(self) -> None:
        """Test that the form saves a meal correctly."""
        eaten_at = timezone.now()
        form_data = {
            "title": "Dinner",
            "category": "DINNER",
            "eaten_at": eaten_at,
            "edibles": [self.bread.pk],
        }
        form = MealForm(data=form_data)
        self.assertTrue(form.is_valid())
        meal = form.save()

        self.assertEqual(meal.title, "Dinner")
        self.assertEqual(meal.category, "DINNER")
        self.assertEqual(meal.edibles.count(), 1)

    def test_form_widgets_have_bootstrap_classes(self) -> None:
        """Test that form widgets have appropriate Bootstrap classes."""
        form = MealForm()
        self.assertIn(
            "form-control", form.fields["title"].widget.attrs.get("class", "")
        )
        self.assertIn(
            "form-select", form.fields["category"].widget.attrs.get("class", "")
        )

    def test_form_datetime_widget(self) -> None:
        """Test that eaten_at field has a datetime input widget."""
        form = MealForm()
        widget = form.fields["eaten_at"].widget
        self.assertEqual(getattr(widget, "input_type", None), "datetime-local")


class MealViewTestCase(TestCase):
    def setUp(self) -> None:
        self.bread = Edible.objects.create(name="Bread")
        self.cheese = Edible.objects.create(name="Cheese")

    def test_index_view_get(self) -> None:
        """Test GET request to meals index view."""
        response = self.client.get("/meals/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meals/index.html")
        self.assertIn("form", response.context)
        self.assertIn("meals", response.context)

    def test_index_view_post_valid(self) -> None:
        """Test POST request with valid data creates a meal."""
        eaten_at = timezone.now()
        post_data = {
            "title": "Test Meal",
            "category": "BREAKFAST",
            "eaten_at": eaten_at.strftime("%Y-%m-%dT%H:%M"),
            "edibles": [self.bread.pk, self.cheese.pk],
        }
        response = self.client.post("/meals/", post_data)

        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(Meal.objects.count(), 1)
        meal = Meal.objects.first()
        self.assertIsNotNone(meal)
        assert meal is not None  # Type narrowing for mypy
        self.assertEqual(meal.title, "Test Meal")
        self.assertEqual(meal.category, "BREAKFAST")
        self.assertEqual(meal.edibles.count(), 2)

    def test_index_view_post_invalid(self) -> None:
        """Test POST request with invalid data shows errors."""
        post_data = {
            "title": "",  # Empty title should be invalid
            "category": "LUNCH",
        }
        response = self.client.post("/meals/", post_data)

        self.assertEqual(response.status_code, 200)  # Stay on same page
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn("title", response.context["form"].errors)
        self.assertEqual(Meal.objects.count(), 0)

    def test_index_view_meals_ordered_by_eaten_at(self) -> None:
        """Test that meals are ordered by eaten_at (most recent first)."""
        earlier = timezone.make_aware(datetime(2025, 9, 29, 10, 0))
        later = timezone.make_aware(datetime(2025, 9, 30, 12, 0))

        Meal.objects.create(
            title="Earlier Meal", category="BREAKFAST", eaten_at=earlier
        )
        Meal.objects.create(title="Later Meal", category="LUNCH", eaten_at=later)

        response = self.client.get("/meals/")
        meals = response.context["meals"]

        self.assertEqual(meals[0].title, "Later Meal")
        self.assertEqual(meals[1].title, "Earlier Meal")

    def test_index_view_limits_meals_display(self) -> None:
        """Test that index view limits number of meals displayed."""
        eaten_at = timezone.now()
        # Create more than 10 meals
        for i in range(15):
            Meal.objects.create(
                title=f"Meal {i}",
                category="SNACK",
                eaten_at=eaten_at,
            )

        response = self.client.get("/meals/")
        meals = response.context["meals"]

        # Should only show latest 10
        self.assertEqual(len(meals), 10)
