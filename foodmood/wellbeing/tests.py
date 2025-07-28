from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from .models import WellbeingEntry, WellbeingParameter


class WellbeingParameterModelTest(TestCase):
    """Test cases for WellbeingParameter model"""

    def setUp(self) -> None:
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpass123"
        )

    def test_create_categoric_parameter(self) -> None:
        """Test creating a valid categoric parameter"""
        param = WellbeingParameter.objects.create(
            user=self.user1,
            name="Mood",
            type=WellbeingParameter.ParameterType.CATEGORIC,
            options=["Happy", "Neutral", "Sad"],
            description="Daily mood tracking",
        )

        self.assertEqual(param.user, self.user1)
        self.assertEqual(param.name, "Mood")
        self.assertEqual(param.type, WellbeingParameter.ParameterType.CATEGORIC)
        self.assertEqual(param.options, ["Happy", "Neutral", "Sad"])
        self.assertEqual(param.description, "Daily mood tracking")
        self.assertIsNotNone(param.creation_date)
        self.assertIsNotNone(param.update_date)

    def test_create_numeric_parameter(self) -> None:
        """Test creating a valid numeric parameter"""
        param = WellbeingParameter.objects.create(
            user=self.user1,
            name="Energy Level",
            type=WellbeingParameter.ParameterType.NUMERIC,
            description="Energy level from 1-10",
        )

        self.assertEqual(param.user, self.user1)
        self.assertEqual(param.name, "Energy Level")
        self.assertEqual(param.type, WellbeingParameter.ParameterType.NUMERIC)
        self.assertIsNone(param.options)
        self.assertEqual(param.description, "Energy level from 1-10")

    def test_str_representation(self) -> None:
        """Test string representation of WellbeingParameter"""
        param = WellbeingParameter.objects.create(
            user=self.user1,
            name="Test Parameter",
            type=WellbeingParameter.ParameterType.NUMERIC,
        )

        expected = f"{self.user1.username} - Test Parameter (numeric)"
        self.assertEqual(str(param), expected)

    def test_unique_together_constraint_same_user(self) -> None:
        """Test that parameter names must be unique per user"""
        WellbeingParameter.objects.create(
            user=self.user1,
            name="Mood",
            type=WellbeingParameter.ParameterType.CATEGORIC,
            options=["Happy", "Sad"],
        )

        # Same name for same user should fail
        with self.assertRaises(IntegrityError):
            WellbeingParameter.objects.create(
                user=self.user1,
                name="Mood",
                type=WellbeingParameter.ParameterType.NUMERIC,
            )

    def test_unique_together_constraint_different_user(self) -> None:
        """Test that same parameter names are allowed for different users"""
        WellbeingParameter.objects.create(
            user=self.user1,
            name="Mood",
            type=WellbeingParameter.ParameterType.CATEGORIC,
            options=["Happy", "Sad"],
        )

        # Same name for different user should succeed
        param2 = WellbeingParameter.objects.create(
            user=self.user2,
            name="Mood",
            type=WellbeingParameter.ParameterType.NUMERIC,
        )
        self.assertEqual(param2.name, "Mood")
        self.assertEqual(param2.user, self.user2)

    def test_categoric_parameter_validation_no_options(self) -> None:
        """Test validation fails for categoric parameter without options"""
        param = WellbeingParameter(
            user=self.user1,
            name="Mood",
            type=WellbeingParameter.ParameterType.CATEGORIC,
            options=None,
        )

        with self.assertRaises(ValidationError) as context:
            param.full_clean()

        self.assertIn("options", context.exception.message_dict)
        self.assertIn("must have at least one option", str(context.exception))

    def test_categoric_parameter_validation_empty_options(self) -> None:
        """Test validation fails for categoric parameter with empty options"""
        param = WellbeingParameter(
            user=self.user1,
            name="Mood",
            type=WellbeingParameter.ParameterType.CATEGORIC,
            options=[],
        )

        with self.assertRaises(ValidationError) as context:
            param.full_clean()

        self.assertIn("options", context.exception.message_dict)

    def test_categoric_parameter_validation_non_list_options(self) -> None:
        """Test validation fails for categoric parameter with non-list options"""
        param = WellbeingParameter(
            user=self.user1,
            name="Mood",
            type=WellbeingParameter.ParameterType.CATEGORIC,
            options="not a list",
        )

        with self.assertRaises(ValidationError) as context:
            param.full_clean()

        self.assertIn("options", context.exception.message_dict)

    def test_numeric_parameter_validation_with_options(self) -> None:
        """Test validation fails for numeric parameter with options"""
        param = WellbeingParameter(
            user=self.user1,
            name="Energy Level",
            type=WellbeingParameter.ParameterType.NUMERIC,
            options=["1", "2", "3"],
        )

        with self.assertRaises(ValidationError) as context:
            param.full_clean()

        self.assertIn("options", context.exception.message_dict)
        self.assertIn("should not have options", str(context.exception))

    def test_parameter_ordering(self) -> None:
        """Test that parameters are ordered by name"""
        WellbeingParameter.objects.create(
            user=self.user1,
            name="Zebra",
            type=WellbeingParameter.ParameterType.NUMERIC,
        )
        WellbeingParameter.objects.create(
            user=self.user1,
            name="Alpha",
            type=WellbeingParameter.ParameterType.NUMERIC,
        )

        params = list(WellbeingParameter.objects.all())
        self.assertEqual(params[0].name, "Alpha")
        self.assertEqual(params[1].name, "Zebra")


class WellbeingEntryModelTest(TestCase):
    """Test cases for WellbeingEntry model"""

    def setUp(self) -> None:
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpass123"
        )

        self.categoric_param = WellbeingParameter.objects.create(
            user=self.user1,
            name="Mood",
            type=WellbeingParameter.ParameterType.CATEGORIC,
            options=["Happy", "Neutral", "Sad"],
        )

        self.numeric_param = WellbeingParameter.objects.create(
            user=self.user1,
            name="Energy Level",
            type=WellbeingParameter.ParameterType.NUMERIC,
        )

    def test_create_categoric_entry(self) -> None:
        """Test creating a valid categoric entry"""
        entry = WellbeingEntry.objects.create(
            user=self.user1,
            parameter=self.categoric_param,
            categoric_value="Happy",
            notes="Feeling great today!",
        )

        self.assertEqual(entry.user, self.user1)
        self.assertEqual(entry.parameter, self.categoric_param)
        self.assertEqual(entry.categoric_value, "Happy")
        self.assertIsNone(entry.numeric_value)
        self.assertEqual(entry.notes, "Feeling great today!")
        self.assertIsNotNone(entry.date_time)
        self.assertIsNotNone(entry.creation_date)

    def test_create_numeric_entry(self) -> None:
        """Test creating a valid numeric entry"""
        entry = WellbeingEntry.objects.create(
            user=self.user1,
            parameter=self.numeric_param,
            numeric_value=Decimal("7.5"),
            notes="Good energy today",
        )

        self.assertEqual(entry.user, self.user1)
        self.assertEqual(entry.parameter, self.numeric_param)
        self.assertEqual(entry.numeric_value, Decimal("7.5"))
        self.assertIsNone(entry.categoric_value)
        self.assertEqual(entry.notes, "Good energy today")

    def test_str_representation(self) -> None:
        """Test string representation of WellbeingEntry"""
        entry = WellbeingEntry.objects.create(
            user=self.user1,
            parameter=self.categoric_param,
            categoric_value="Happy",
        )

        expected_start = f"{self.user1.username} - {self.categoric_param.name}: Happy"
        self.assertTrue(str(entry).startswith(expected_start))

    def test_entry_ordering(self) -> None:
        """Test that entries are ordered by date_time descending"""
        # Create entries with specific times
        older_time = timezone.now() - timezone.timedelta(hours=1)
        newer_time = timezone.now()

        entry1 = WellbeingEntry.objects.create(
            user=self.user1,
            parameter=self.categoric_param,
            categoric_value="Happy",
            date_time=older_time,
        )
        entry2 = WellbeingEntry.objects.create(
            user=self.user1,
            parameter=self.categoric_param,
            categoric_value="Sad",
            date_time=newer_time,
        )

        entries = list(WellbeingEntry.objects.all())
        self.assertEqual(entries[0], entry2)  # Newer entry first
        self.assertEqual(entries[1], entry1)  # Older entry second

    def test_user_parameter_mismatch_validation(self) -> None:
        """Test validation fails when entry user doesn't match parameter user"""
        entry = WellbeingEntry(
            user=self.user2,  # Different user
            parameter=self.categoric_param,  # Belongs to user1
            categoric_value="Happy",
        )

        with self.assertRaises(ValidationError) as context:
            entry.full_clean()

        self.assertIn("parameter", context.exception.message_dict)
        self.assertIn("same user", str(context.exception))

    def test_categoric_entry_validation_no_value(self) -> None:
        """Test validation fails for categoric entry without categoric_value"""
        entry = WellbeingEntry(
            user=self.user1,
            parameter=self.categoric_param,
            categoric_value=None,
        )

        with self.assertRaises(ValidationError) as context:
            entry.full_clean()

        self.assertIn("categoric_value", context.exception.message_dict)

    def test_categoric_entry_validation_with_numeric_value(self) -> None:
        """Test validation fails for categoric entry with numeric_value"""
        entry = WellbeingEntry(
            user=self.user1,
            parameter=self.categoric_param,
            categoric_value="Happy",
            numeric_value=Decimal("5.0"),
        )

        with self.assertRaises(ValidationError) as context:
            entry.full_clean()

        self.assertIn("numeric_value", context.exception.message_dict)
        self.assertIn("should not have a numeric_value", str(context.exception))

    def test_categoric_entry_validation_invalid_option(self) -> None:
        """Test validation fails for categoric entry with invalid option"""
        entry = WellbeingEntry(
            user=self.user1,
            parameter=self.categoric_param,
            categoric_value="Excited",  # Not in options
        )

        with self.assertRaises(ValidationError) as context:
            entry.full_clean()

        self.assertIn("categoric_value", context.exception.message_dict)
        self.assertIn("must be one of", str(context.exception))

    def test_numeric_entry_validation_no_value(self) -> None:
        """Test validation fails for numeric entry without numeric_value"""
        entry = WellbeingEntry(
            user=self.user1,
            parameter=self.numeric_param,
            numeric_value=None,
        )

        with self.assertRaises(ValidationError) as context:
            entry.full_clean()

        self.assertIn("numeric_value", context.exception.message_dict)

    def test_numeric_entry_validation_with_categoric_value(self) -> None:
        """Test validation fails for numeric entry with categoric_value"""
        entry = WellbeingEntry(
            user=self.user1,
            parameter=self.numeric_param,
            numeric_value=Decimal("7.5"),
            categoric_value="Happy",
        )

        with self.assertRaises(ValidationError) as context:
            entry.full_clean()

        self.assertIn("categoric_value", context.exception.message_dict)
        self.assertIn("should not have a categoric_value", str(context.exception))

    def test_valid_categoric_entry_with_all_options(self) -> None:
        """Test that all valid options work for categoric entries"""
        # Get options with type checking workaround
        options = self.categoric_param.options
        if options is not None and isinstance(options, list):  # type: ignore[unreachable]
            for option in options:  # type: ignore[unreachable]
                entry = WellbeingEntry(
                    user=self.user1,
                    parameter=self.categoric_param,
                    categoric_value=option,
                )
                # Should not raise ValidationError
                entry.full_clean()

    def test_numeric_entry_decimal_precision(self) -> None:
        """Test numeric entry handles decimal precision correctly"""
        entry = WellbeingEntry.objects.create(
            user=self.user1,
            parameter=self.numeric_param,
            numeric_value=Decimal("123.45"),
        )

        self.assertEqual(entry.numeric_value, Decimal("123.45"))

    def test_entry_with_custom_datetime(self) -> None:
        """Test creating entry with custom datetime"""
        custom_time = timezone.now() - timezone.timedelta(days=1)
        entry = WellbeingEntry.objects.create(
            user=self.user1,
            parameter=self.categoric_param,
            categoric_value="Neutral",
            date_time=custom_time,
        )

        self.assertEqual(entry.date_time, custom_time)

    def test_related_name_relationships(self) -> None:
        """Test that related names work correctly"""
        # Test parameter -> entries relationship
        entry1 = WellbeingEntry.objects.create(
            user=self.user1,
            parameter=self.categoric_param,
            categoric_value="Happy",
        )
        entry2 = WellbeingEntry.objects.create(
            user=self.user1,
            parameter=self.categoric_param,
            categoric_value="Sad",
        )

        related_entries = self.categoric_param.entries.all()  # type: ignore[attr-defined]
        self.assertIn(entry1, related_entries)
        self.assertIn(entry2, related_entries)

        # Test user -> wellbeing_entries relationship
        user_entries = self.user1.wellbeing_entries.all()  # type: ignore[attr-defined]
        self.assertIn(entry1, user_entries)
        self.assertIn(entry2, user_entries)

        # Test user -> wellbeing_parameters relationship
        user_params = self.user1.wellbeing_parameters.all()  # type: ignore[attr-defined]
        self.assertIn(self.categoric_param, user_params)
        self.assertIn(self.numeric_param, user_params)
