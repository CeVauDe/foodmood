from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from recipes.models import Ingredient, Recipe, RecipeIngredient

from .forms import MealForm
from .models import Meal


class MealModelTest(TestCase):
    """Test cases for the Meal model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.ingredient = Ingredient.objects.create(name="Chicken Breast")
        self.recipe = Recipe.objects.create(name="Grilled Chicken")
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient, weight_g=Decimal("200.00")
        )

    def test_create_meal(self) -> None:
        """Test creating a basic meal."""
        meal_time = timezone.now()
        meal = Meal.objects.create(
            name="Lunch", date_time=meal_time, user=self.user, notes="Post-workout meal"
        )

        self.assertEqual(meal.name, "Lunch")
        self.assertEqual(meal.date_time, meal_time)
        self.assertEqual(meal.user, self.user)
        self.assertEqual(meal.notes, "Post-workout meal")
        self.assertIsNotNone(meal.creation_date)
        self.assertIsNotNone(meal.update_date)

    def test_meal_without_notes(self) -> None:
        """Test creating a meal without notes."""
        meal = Meal.objects.create(
            name="Breakfast", date_time=timezone.now(), user=self.user
        )

        self.assertEqual(meal.name, "Breakfast")
        self.assertIsNone(meal.notes)

    def test_meal_with_recipes(self) -> None:
        """Test adding recipes to a meal."""
        meal = Meal.objects.create(
            name="Dinner", date_time=timezone.now(), user=self.user
        )

        meal.recipes.add(self.recipe)

        self.assertEqual(meal.recipes.count(), 1)
        self.assertIn(self.recipe, meal.recipes.all())

    def test_meal_str_representation(self) -> None:
        """Test the string representation of a meal."""
        meal_time = datetime(
            2025, 1, 15, 12, 30, tzinfo=timezone.get_current_timezone()
        )
        meal = Meal.objects.create(name="Lunch", date_time=meal_time, user=self.user)

        expected_str = "Lunch - testuser (2025-01-15 12:30)"
        self.assertEqual(str(meal), expected_str)

    def test_meal_user_relationship(self) -> None:
        """Test the relationship between meal and user."""
        meal1 = Meal.objects.create(
            name="Breakfast", date_time=timezone.now(), user=self.user
        )
        meal2 = Meal.objects.create(
            name="Lunch", date_time=timezone.now(), user=self.user
        )

        # Test reverse relationship
        user_meals = Meal.objects.filter(user=self.user)
        self.assertEqual(user_meals.count(), 2)
        self.assertIn(meal1, user_meals)
        self.assertIn(meal2, user_meals)

    def test_meal_ordering(self) -> None:
        """Test that meals are ordered by date_time (newest first)."""
        now = timezone.now()

        meal1 = Meal.objects.create(
            name="Breakfast", date_time=now - timedelta(hours=2), user=self.user
        )
        meal2 = Meal.objects.create(name="Lunch", date_time=now, user=self.user)
        meal3 = Meal.objects.create(
            name="Yesterday Dinner", date_time=now - timedelta(days=1), user=self.user
        )

        meals = list(Meal.objects.all())
        self.assertEqual(meals[0], meal2)  # Lunch (most recent)
        self.assertEqual(meals[1], meal1)  # Breakfast (2 hours ago)
        self.assertEqual(meals[2], meal3)  # Yesterday dinner (oldest)

    def test_meal_cascade_delete_with_user(self) -> None:
        """Test that meals are deleted when user is deleted."""
        meal = Meal.objects.create(
            name="Test Meal", date_time=timezone.now(), user=self.user
        )

        meal_pk = meal.pk
        self.user.delete()

        with self.assertRaises(Meal.DoesNotExist):
            Meal.objects.get(pk=meal_pk)

    def test_meal_multiple_recipes(self) -> None:
        """Test a meal with multiple recipes."""
        recipe2 = Recipe.objects.create(name="Side Salad")

        meal = Meal.objects.create(
            name="Complete Dinner", date_time=timezone.now(), user=self.user
        )

        meal.recipes.add(self.recipe, recipe2)

        self.assertEqual(meal.recipes.count(), 2)
        self.assertIn(self.recipe, meal.recipes.all())
        self.assertIn(recipe2, meal.recipes.all())

    def test_meal_update_date_changes(self) -> None:
        """Test that update_date changes when meal is modified."""
        meal = Meal.objects.create(
            name="Test Meal", date_time=timezone.now(), user=self.user
        )

        original_update_date = meal.update_date

        # Wait a tiny bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        meal.notes = "Updated notes"
        meal.save()

        meal.refresh_from_db()
        self.assertGreater(meal.update_date, original_update_date)


class ModelIntegrationTest(TestCase):
    """Integration tests for all models working together."""

    def setUp(self) -> None:
        """Set up test data for integration tests."""
        self.user = User.objects.create_user(
            username="integrationuser",
            email="integration@example.com",
            password="testpass123",
        )

    def test_complete_meal_creation_workflow(self) -> None:
        """Test the complete workflow of creating a meal with recipes and ingredients."""
        # Create ingredients
        chicken = Ingredient.objects.create(
            name="Chicken Breast", description="Lean protein"
        )
        rice = Ingredient.objects.create(name="Brown Rice", description="Whole grain")
        vegetables = Ingredient.objects.create(name="Mixed Vegetables")

        # Create recipe
        recipe = Recipe.objects.create(
            name="Healthy Chicken Bowl", notes="Balanced macro meal"
        )

        # Add ingredients to recipe
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=chicken,
            weight_g=Decimal("200.00"),
            notes="Grilled, no oil",
        )
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=rice, weight_g=Decimal("100.00"), notes="Steamed"
        )
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=vegetables, weight_g=Decimal("150.00")
        )

        # Create meal
        meal = Meal.objects.create(
            name="Post-Workout Lunch",
            date_time=timezone.now(),
            user=self.user,
            notes="Feeling energized after gym",
        )

        # Add recipe to meal
        meal.recipes.add(recipe)

        # Verify the complete structure
        self.assertEqual(meal.recipes.count(), 1)
        self.assertEqual(recipe.ingredients.count(), 3)

        # Test querying through relationships
        meal_ingredients = []
        for recipe in meal.recipes.all():
            for recipe_ingredient in RecipeIngredient.objects.filter(recipe=recipe):
                meal_ingredients.append(recipe_ingredient.ingredient)

        self.assertEqual(len(meal_ingredients), 3)
        self.assertIn(chicken, meal_ingredients)
        self.assertIn(rice, meal_ingredients)
        self.assertIn(vegetables, meal_ingredients)

    def test_multiple_users_independent_meals(self) -> None:
        """Test that different users can have independent meals."""
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

        # Create shared ingredients and recipes (global)
        ingredient = Ingredient.objects.create(name="Shared Ingredient")
        recipe = Recipe.objects.create(name="Shared Recipe")
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient)

        # Create meals for both users
        meal1 = Meal.objects.create(
            name="User 1 Meal", date_time=timezone.now(), user=self.user
        )
        meal2 = Meal.objects.create(
            name="User 2 Meal", date_time=timezone.now(), user=user2
        )

        meal1.recipes.add(recipe)
        meal2.recipes.add(recipe)

        # Verify each user only sees their own meals
        user1_meals = Meal.objects.filter(user=self.user)
        user2_meals = Meal.objects.filter(user=user2)

        self.assertEqual(user1_meals.count(), 1)
        self.assertEqual(user2_meals.count(), 1)
        self.assertNotEqual(user1_meals.first(), user2_meals.first())

        # But they can share the same recipes and ingredients
        self.assertEqual(meal1.recipes.first(), meal2.recipes.first())


class MealFormTest(TestCase):
    """Test cases for the MealForm."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.ingredient = Ingredient.objects.create(name="Test Ingredient")
        self.recipe = Recipe.objects.create(name="Test Recipe")
        RecipeIngredient.objects.create(recipe=self.recipe, ingredient=self.ingredient)

    def test_meal_form_valid_data(self) -> None:
        """Test MealForm with valid data."""
        current_time = timezone.now()
        form_data = {
            "name": "Test Meal",
            "meal_date": current_time.date(),
            "meal_time": current_time.time(),
            "notes": "Test notes",
        }
        form = MealForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_meal_form_valid_with_recipes(self) -> None:
        """Test MealForm with recipes selected."""
        current_time = timezone.now()
        form_data = {
            "name": "Test Meal",
            "meal_date": current_time.date(),
            "meal_time": current_time.time(),
            "recipes": [self.recipe.pk],
            "notes": "Test notes",
        }
        form = MealForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_meal_form_missing_required_fields(self) -> None:
        """Test MealForm with missing required fields."""
        form_data = {"notes": "Test notes"}
        form = MealForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        # Date and time are not required individually since clean() handles defaults

    def test_meal_form_empty_name(self) -> None:
        """Test MealForm with empty name."""
        current_time = timezone.now()
        form_data = {
            "name": "",
            "meal_date": current_time.date(),
            "meal_time": current_time.time(),
            "notes": "Test notes",
        }
        form = MealForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_meal_form_recipes_not_required(self) -> None:
        """Test that recipes field is not required."""
        current_time = timezone.now()
        form_data = {
            "name": "Test Meal",
            "meal_date": current_time.date(),
            "meal_time": current_time.time(),
            "notes": "Test notes",
        }
        form = MealForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.fields["recipes"].required)

    def test_meal_form_date_only(self) -> None:
        """Test MealForm with only date provided (time should default)."""
        current_time = timezone.now()
        form_data = {
            "name": "Test Meal",
            "meal_date": current_time.date(),
            # No meal_time provided
            "notes": "Test notes",
        }
        form = MealForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertIn("date_time", form.cleaned_data)

    def test_meal_form_time_only(self) -> None:
        """Test MealForm with only time provided (date should default)."""
        current_time = timezone.now()
        form_data = {
            "name": "Test Meal",
            # No meal_date provided
            "meal_time": current_time.time(),
            "notes": "Test notes",
        }
        form = MealForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertIn("date_time", form.cleaned_data)

    def test_meal_form_combines_date_time_correctly(self) -> None:
        """Test that MealForm correctly combines date and time fields."""
        test_date = timezone.now().date()
        test_time = timezone.now().time()
        form_data = {
            "name": "Test Meal",
            "meal_date": test_date,
            "meal_time": test_time,
            "notes": "Test notes",
        }
        form = MealForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Check that date_time is properly combined
        combined_datetime = form.cleaned_data["date_time"]
        self.assertEqual(combined_datetime.date(), test_date)
        self.assertEqual(combined_datetime.time(), test_time)


class MealViewTest(TestCase):
    """Test cases for meal views."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        self.ingredient = Ingredient.objects.create(name="Test Ingredient")
        self.recipe = Recipe.objects.create(name="Test Recipe")
        RecipeIngredient.objects.create(recipe=self.recipe, ingredient=self.ingredient)

    def test_meals_index_view_authenticated(self) -> None:
        """Test meals index view for authenticated user."""
        response = self.client.get(reverse("meals:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Meals")
        self.assertContains(response, "Add Meal")

    def test_meals_index_view_unauthenticated(self) -> None:
        """Test meals index view for unauthenticated user."""
        self.client.logout()
        response = self.client.get(reverse("meals:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Meals")
        self.assertContains(response, "Login")

    def test_meals_index_view_with_recent_meals(self) -> None:
        """Test meals index view shows recent meals."""
        # Create some meals
        Meal.objects.create(
            name="Breakfast",
            date_time=timezone.now() - timedelta(hours=1),
            user=self.user,
            notes="Morning meal",
        )
        Meal.objects.create(
            name="Lunch",
            date_time=timezone.now(),
            user=self.user,
        )

        response = self.client.get(reverse("meals:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Breakfast")
        self.assertContains(response, "Lunch")
        self.assertContains(response, "Morning meal")

    def test_create_meal_view_authenticated_get(self) -> None:
        """Test create meal view GET request for authenticated user."""
        response = self.client.get(reverse("meals:create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add New Meal")
        self.assertContains(response, "Meal Name")
        self.assertContains(response, "Date")
        self.assertContains(response, "Time")

    def test_create_meal_view_unauthenticated(self) -> None:
        """Test create meal view redirects unauthenticated users."""
        self.client.logout()
        response = self.client.get(reverse("meals:create"))
        self.assertEqual(response.status_code, 302)
        # Check that it redirects to a login URL (Django default is /accounts/login/)
        location = response.get("Location", "")
        self.assertTrue(location.startswith("/accounts/login/"))

    def test_create_meal_view_valid_post(self) -> None:
        """Test create meal view with valid POST data."""
        meal_time = timezone.now()
        post_data = {
            "name": "Test Meal",
            "meal_date": meal_time.strftime("%Y-%m-%d"),
            "meal_time": meal_time.strftime("%H:%M"),
            "notes": "Test notes",
        }

        response = self.client.post(reverse("meals:create"), data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("meals:index"))

        # Check meal was created
        meal = Meal.objects.get(name="Test Meal")
        self.assertEqual(meal.user, self.user)
        self.assertEqual(meal.notes, "Test notes")

    def test_create_meal_view_with_recipes(self) -> None:
        """Test create meal view with recipes selected."""
        meal_time = timezone.now()
        post_data = {
            "name": "Test Meal with Recipe",
            "meal_date": meal_time.strftime("%Y-%m-%d"),
            "meal_time": meal_time.strftime("%H:%M"),
            "recipes": [self.recipe.pk],
            "notes": "Test notes",
        }

        response = self.client.post(reverse("meals:create"), data=post_data)
        self.assertEqual(response.status_code, 302)

        # Check meal was created with recipe
        meal = Meal.objects.get(name="Test Meal with Recipe")
        self.assertEqual(meal.recipes.count(), 1)
        self.assertIn(self.recipe, meal.recipes.all())

    def test_create_meal_view_invalid_post(self) -> None:
        """Test create meal view with invalid POST data."""
        post_data = {
            "name": "",  # Empty name should be invalid
            "meal_date": "",  # Empty meal_date should be invalid
            "meal_time": "",  # Empty meal_time should be invalid
        }

        response = self.client.post(reverse("meals:create"), data=post_data)
        self.assertEqual(response.status_code, 200)  # Should stay on form page
        self.assertContains(response, "Add New Meal")

        # Check no meal was created
        self.assertEqual(Meal.objects.count(), 0)

    def test_meals_index_view_user_isolation(self) -> None:
        """Test that users only see their own meals."""
        # Create another user and meal
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        Meal.objects.create(
            name="Other User Meal",
            date_time=timezone.now(),
            user=other_user,
        )

        # Create meal for current user
        Meal.objects.create(
            name="My Meal",
            date_time=timezone.now(),
            user=self.user,
        )

        response = self.client.get(reverse("meals:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Meal")
        self.assertNotContains(response, "Other User Meal")
