from django.db import models


class Ingredient(models.Model):
    """
    Master list of ingredients that can be part of meals.
    Global ingredients shared across all users.
    """

    name: models.CharField = models.CharField(max_length=200, unique=True)
    description: models.TextField = models.TextField(blank=True, null=True)
    creation_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return str(self.name)


class Recipe(models.Model):
    """
    A collection of ingredients with quantities.
    Global recipes shared across all users.
    """

    name: models.CharField = models.CharField(max_length=200)
    ingredients: models.ManyToManyField = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", related_name="recipes"
    )
    notes: models.TextField = models.TextField(blank=True, null=True)
    creation_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["creation_date"]),
        ]

    def __str__(self) -> str:
        return str(self.name)


class RecipeIngredient(models.Model):
    """
    Through model for Recipe-Ingredient many-to-many relationship.
    Stores the quantity and notes for each ingredient in a recipe.
    """

    recipe: models.ForeignKey = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient: models.ForeignKey = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE
    )
    weight_g: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in grams",
    )
    notes: models.TextField = models.TextField(
        blank=True,
        null=True,
        help_text="Specific notes about this ingredient in this recipe",
    )

    class Meta:
        unique_together = ["recipe", "ingredient"]

    def __str__(self) -> str:
        weight_str = f" ({self.weight_g}g)" if self.weight_g else ""
        return f"{str(self.recipe.name)} - {str(self.ingredient.name)}{weight_str}"
