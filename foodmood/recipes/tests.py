from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from .models import Ingredient, Recipe, RecipeIngredient


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
