from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Edible


class IngredientsTestCase(TestCase):
    def setUp(self) -> None:
        # Create edibles
        oil = Edible.objects.create(name="Oil")
        vinegar = Edible.objects.create(name="Vinegar")
        salt = Edible.objects.create(name="Salt")
        pepper = Edible.objects.create(name="Pepper")
        dressing = Edible.objects.create(name="Dressing")
        cucumber = Edible.objects.create(name="Cucumber")
        lettuce = Edible.objects.create(name="Lettuce")
        salad = Edible.objects.create(name="Mixed Salad")

        # Set ingredients
        dressing.ingredients.set([oil, vinegar, salt, pepper])
        salad.ingredients.set([dressing, cucumber, lettuce])

    def test_ingredients_count(self) -> None:
        dressing = Edible.objects.get(name="Dressing")
        self.assertEqual(dressing.ingredients.count(), 4)

        salad = Edible.objects.get(name="Mixed Salad")
        self.assertEqual(salad.ingredients.count(), 3)

    def test_used_in_count(self) -> None:
        dressing = Edible.objects.get(name="Dressing")
        self.assertEqual(dressing.used_in.count(), 1)

    def test_ingredients_count_of_ingredient(self) -> None:
        salad = Edible.objects.get(name="Mixed Salad")
        self.assertEqual(salad.ingredients.get(name="Dressing").ingredients.count(), 4)

    def test_edible_cannot_have_itself_as_ingredient(self) -> None:
        e1 = Edible.objects.create(name="e1")

        with self.assertRaises(ValidationError):
            e1.ingredients.set([e1])
            e1.full_clean()
