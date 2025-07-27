from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from .models import Ingredient, Meal, Recipe, RecipeIngredient


class IngredientModelTest(TestCase):
    """Test cases for the Ingredient model."""

    def test_create_ingredient(self) -> None:
        """Test creating a basic ingredient."""
        ingredient = Ingredient.objects.create(
            name="Chicken Breast", description="Lean protein source"
        )
        self.assertEqual(ingredient.name, "Chicken Breast")
        self.assertEqual(ingredient.description, "Lean protein source")
        self.assertIsNotNone(ingredient.creation_date)

    def test_create_ingredient_without_description(self) -> None:
        """Test creating an ingredient without description."""
        ingredient = Ingredient.objects.create(name="Salt")
        self.assertEqual(ingredient.name, "Salt")
        self.assertIsNone(ingredient.description)

    def test_ingredient_str_representation(self) -> None:
        """Test the string representation of an ingredient."""
        ingredient = Ingredient.objects.create(name="Olive Oil")
        self.assertEqual(str(ingredient), "Olive Oil")

    def test_ingredient_name_unique_constraint(self) -> None:
        """Test that ingredient names must be unique."""
        Ingredient.objects.create(name="Tomato")
        with self.assertRaises(IntegrityError):
            Ingredient.objects.create(name="Tomato")

    def test_ingredient_ordering(self) -> None:
        """Test that ingredients are ordered by name."""
        Ingredient.objects.create(name="Zucchini")
        Ingredient.objects.create(name="Apple")
        Ingredient.objects.create(name="Banana")

        ingredients = list(Ingredient.objects.all())
        self.assertEqual(ingredients[0].name, "Apple")
        self.assertEqual(ingredients[1].name, "Banana")
        self.assertEqual(ingredients[2].name, "Zucchini")


class RecipeModelTest(TestCase):
    """Test cases for the Recipe model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.ingredient1 = Ingredient.objects.create(name="Chicken Breast")
        self.ingredient2 = Ingredient.objects.create(name="Rice")
        self.ingredient3 = Ingredient.objects.create(name="Broccoli")

    def test_create_recipe(self) -> None:
        """Test creating a basic recipe."""
        recipe = Recipe.objects.create(
            name="Chicken and Rice", notes="Healthy balanced meal"
        )
        self.assertEqual(recipe.name, "Chicken and Rice")
        self.assertEqual(recipe.notes, "Healthy balanced meal")
        self.assertIsNotNone(recipe.creation_date)

    def test_recipe_without_notes(self) -> None:
        """Test creating a recipe without notes."""
        recipe = Recipe.objects.create(name="Simple Salad")
        self.assertEqual(recipe.name, "Simple Salad")
        self.assertIsNone(recipe.notes)

    def test_recipe_str_representation(self) -> None:
        """Test the string representation of a recipe."""
        recipe = Recipe.objects.create(name="Pasta Bolognese")
        self.assertEqual(str(recipe), "Pasta Bolognese")

    def test_recipe_many_to_many_with_ingredients(self) -> None:
        """Test adding ingredients to a recipe through RecipeIngredient."""
        recipe = Recipe.objects.create(name="Chicken Bowl")

        # Add ingredients through the through model
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=self.ingredient1,
            weight_g=Decimal("200.00"),
            notes="Grilled",
        )
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=self.ingredient2, weight_g=Decimal("150.00")
        )

        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(self.ingredient1, recipe.ingredients.all())
        self.assertIn(self.ingredient2, recipe.ingredients.all())

    def test_recipe_ordering(self) -> None:
        """Test that recipes are ordered by name."""
        Recipe.objects.create(name="Zucchini Pasta")
        Recipe.objects.create(name="Apple Pie")
        Recipe.objects.create(name="Banana Bread")

        recipes = list(Recipe.objects.all())
        self.assertEqual(recipes[0].name, "Apple Pie")
        self.assertEqual(recipes[1].name, "Banana Bread")
        self.assertEqual(recipes[2].name, "Zucchini Pasta")


class RecipeIngredientModelTest(TestCase):
    """Test cases for the RecipeIngredient through model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.ingredient = Ingredient.objects.create(name="Chicken Breast")
        self.recipe = Recipe.objects.create(name="Grilled Chicken")

    def test_create_recipe_ingredient(self) -> None:
        """Test creating a recipe-ingredient relationship."""
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            weight_g=Decimal("250.00"),
            notes="Season with salt and pepper",
        )

        self.assertEqual(recipe_ingredient.recipe, self.recipe)
        self.assertEqual(recipe_ingredient.ingredient, self.ingredient)
        self.assertEqual(recipe_ingredient.weight_g, Decimal("250.00"))
        self.assertEqual(recipe_ingredient.notes, "Season with salt and pepper")

    def test_recipe_ingredient_without_weight(self) -> None:
        """Test creating a recipe-ingredient without weight."""
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient, notes="To taste"
        )

        self.assertIsNone(recipe_ingredient.weight_g)
        self.assertEqual(recipe_ingredient.notes, "To taste")

    def test_recipe_ingredient_without_notes(self) -> None:
        """Test creating a recipe-ingredient without notes."""
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient, weight_g=Decimal("100.00")
        )

        self.assertEqual(recipe_ingredient.weight_g, Decimal("100.00"))
        self.assertIsNone(recipe_ingredient.notes)

    def test_recipe_ingredient_str_representation(self) -> None:
        """Test the string representation of recipe-ingredient."""
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient, weight_g=Decimal("200.00")
        )
        expected_str = "Grilled Chicken - Chicken Breast (200.00g)"
        self.assertEqual(str(recipe_ingredient), expected_str)

    def test_recipe_ingredient_str_without_weight(self) -> None:
        """Test string representation without weight."""
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient
        )
        expected_str = "Grilled Chicken - Chicken Breast"
        self.assertEqual(str(recipe_ingredient), expected_str)

    def test_unique_recipe_ingredient_constraint(self) -> None:
        """Test that recipe-ingredient combinations must be unique."""
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient, weight_g=Decimal("100.00")
        )

        with self.assertRaises(IntegrityError):
            RecipeIngredient.objects.create(
                recipe=self.recipe,
                ingredient=self.ingredient,
                weight_g=Decimal("200.00"),
            )


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
