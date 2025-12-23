"""Tests for entries models."""
import pytest
from decimal import Decimal
from django.utils import timezone

from entries.models import CorrectionScale, GlucoseReading, InsulinDose, InsulinType, Meal
from base.middleware import set_current_user


class TestInsulinType:
    """Tests for InsulinType model."""

    def test_create_insulin_type(self, user):
        """Test creating an insulin type."""
        set_current_user(user)
        insulin_type = InsulinType.objects.create(
            name="Long-Acting",
            type=InsulinType.Type.LONG_ACTING,
            notes="Long-acting insulin"
        )
        set_current_user(None)
        
        assert insulin_type.name == "Long-Acting"
        assert insulin_type.type == InsulinType.Type.LONG_ACTING
        assert insulin_type.notes == "Long-acting insulin"
        assert insulin_type.is_default is False
        assert insulin_type.last_modified_by == user

    def test_insulin_type_str(self, insulin_type):
        """Test string representation of insulin type."""
        assert str(insulin_type) == "Rapid-acting"

    def test_is_default_only_one(self, user):
        """Test that only one insulin type can be default."""
        set_current_user(user)
        
        type1 = InsulinType.objects.create(name="Type 1", is_default=True)
        assert type1.is_default is True
        
        type2 = InsulinType.objects.create(name="Type 2", is_default=True)
        
        # Refresh type1 from database
        type1.refresh_from_db()
        
        # Only type2 should be default now
        assert type1.is_default is False
        assert type2.is_default is True
        
        set_current_user(None)

    def test_last_modified_by_auto_set(self, user):
        """Test that last_modified_by is automatically set."""
        set_current_user(user)
        
        insulin_type = InsulinType.objects.create(name="Auto Test")
        
        set_current_user(None)
        
        assert insulin_type.last_modified_by == user

    def test_last_modified_by_explicit_override(self, user, second_user):
        """Test that explicitly setting last_modified_by works."""
        set_current_user(user)
        
        insulin_type = InsulinType.objects.create(
            name="Explicit Test",
            last_modified_by=second_user
        )
        
        set_current_user(None)
        
        # Should use the explicitly set user
        assert insulin_type.last_modified_by == second_user

    def test_insulin_type_choices(self, user):
        """Test that all insulin type choices can be created."""
        set_current_user(user)
        
        # Test each type choice
        for type_value, type_label in InsulinType.Type.choices:
            insulin_type = InsulinType.objects.create(
                name=f"{type_label} Test",
                type=type_value
            )
            assert insulin_type.type == type_value
            assert insulin_type.get_type_display() == type_label
        
        set_current_user(None)


class TestGlucoseReading:
    """Tests for GlucoseReading model."""

    def test_create_glucose_reading(self, user):
        """Test creating a glucose reading."""
        set_current_user(user)
        
        reading = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.6"),
            unit="mmol/L",
            notes="Before breakfast"
        )
        
        set_current_user(None)
        
        assert reading.value == Decimal("5.6")
        assert reading.unit == "mmol/L"
        assert reading.notes == "Before breakfast"
        assert reading.last_modified_by == user

    def test_glucose_reading_str(self, user):
        """Test string representation of glucose reading."""
        set_current_user(user)
        
        occurred_at = timezone.make_aware(timezone.datetime(2025, 12, 22, 10, 30))
        reading = GlucoseReading.objects.create(
            occurred_at=occurred_at,
            value=Decimal("6.2"),
            unit="mmol/L"
        )
        
        set_current_user(None)
        
        assert str(reading) == "6.2 mmol/L at 2025-12-22 10:30:00+00:00"

    def test_glucose_reading_units(self, user):
        """Test different unit choices."""
        set_current_user(user)
        
        reading_mmol = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.5"),
            unit="mmol/L"
        )
        
        reading_mgdl = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("100.0"),
            unit="mg/dL"
        )
        
        set_current_user(None)
        
        assert reading_mmol.unit == "mmol/L"
        assert reading_mgdl.unit == "mg/dL"


class TestInsulinDose:
    """Tests for InsulinDose model."""

    def test_create_insulin_dose(self, user, insulin_type):
        """Test creating an insulin dose."""
        set_current_user(user)
        
        dose = InsulinDose.objects.create(
            occurred_at=timezone.now(),
            base_units=Decimal("10.50"),
            correction_units=Decimal("2.00"),
            insulin_type=insulin_type,
            notes="With meal"
        )
        
        set_current_user(None)
        
        assert dose.base_units == Decimal("10.50")
        assert dose.correction_units == Decimal("2.00")
        assert dose.insulin_type == insulin_type
        assert dose.notes == "With meal"
        assert dose.last_modified_by == user

    def test_insulin_dose_str(self, user, insulin_type):
        """Test string representation of insulin dose."""
        set_current_user(user)
        
        occurred_at = timezone.make_aware(timezone.datetime(2025, 12, 22, 12, 0))
        dose = InsulinDose.objects.create(
            occurred_at=occurred_at,
            base_units=Decimal("8.00"),
            correction_units=Decimal("1.50"),
            insulin_type=insulin_type
        )
        
        set_current_user(None)
        
        assert str(dose) == "9.50 units (8.00 base + 1.50 correction) of Rapid-acting at 2025-12-22 12:00:00+00:00"

    def test_insulin_dose_requires_insulin_type(self, user):
        """Test that insulin dose requires an insulin type."""
        set_current_user(user)
        
        with pytest.raises(Exception):  # Will raise IntegrityError or similar
            InsulinDose.objects.create(
                occurred_at=timezone.now(),
                base_units=Decimal("5.00"),
                correction_units=Decimal("0.00")
                # Missing insulin_type
            )
        
        set_current_user(None)


class TestMeal:
    """Tests for Meal model."""

    def test_create_meal(self, user):
        """Test creating a meal."""
        set_current_user(user)
        
        meal = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="breakfast",
            description="Oatmeal with berries",
            total_carbs=Decimal("45.0"),
            notes="Felt good after"
        )
        
        set_current_user(None)
        
        assert meal.meal_type == "breakfast"
        assert meal.description == "Oatmeal with berries"
        assert meal.total_carbs == Decimal("45.0")
        assert meal.notes == "Felt good after"
        assert meal.last_modified_by == user

    def test_meal_str(self, user):
        """Test string representation of meal."""
        set_current_user(user)
        
        occurred_at = timezone.make_aware(timezone.datetime(2025, 12, 22, 8, 0))
        meal = Meal.objects.create(
            occurred_at=occurred_at,
            meal_type="breakfast",
            description="Toast and eggs"
        )
        
        set_current_user(None)
        
        assert str(meal) == "Breakfast at 2025-12-22 08:00:00+00:00"

    def test_meal_types(self, user):
        """Test different meal type choices."""
        set_current_user(user)
        
        breakfast = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="breakfast",
            description="Breakfast meal"
        )
        
        lunch = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="lunch",
            description="Lunch meal"
        )
        
        dinner = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="dinner",
            description="Dinner meal"
        )
        
        snack = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="snack",
            description="Snack meal"
        )
        
        set_current_user(None)
        
        assert breakfast.meal_type == "breakfast"
        assert lunch.meal_type == "lunch"
        assert dinner.meal_type == "dinner"
        assert snack.meal_type == "snack"

    def test_meal_optional_carbs(self, user):
        """Test that total_carbs is optional."""
        set_current_user(user)
        
        meal = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="snack",
            description="Coffee"
            # No total_carbs specified
        )
        
        set_current_user(None)
        
        assert meal.total_carbs is None


@pytest.mark.django_db
class TestCorrectionScale:
    """Tests for CorrectionScale model."""

    def test_create_correction_scale(self):
        """Test creating a correction scale entry."""
        scale = CorrectionScale.objects.create(
            greater_than=Decimal("8.0"),
            units_to_add=Decimal("2.0")
        )
        
        assert scale.greater_than == Decimal("8.0")
        assert scale.units_to_add == Decimal("2.0")
        assert scale.id is not None
        assert scale.created_at is not None
        assert scale.updated_at is not None

    def test_correction_scale_str(self):
        """Test string representation of correction scale."""
        scale = CorrectionScale.objects.create(
            greater_than=Decimal("10.5"),
            units_to_add=Decimal("3.5")
        )
        
        assert str(scale) == "Above 10.5: +3.5 units"

    def test_correction_scale_ordering(self):
        """Test that correction scales are ordered by greater_than."""
        scale1 = CorrectionScale.objects.create(
            greater_than=Decimal("10.0"),
            units_to_add=Decimal("2.0")
        )
        scale2 = CorrectionScale.objects.create(
            greater_than=Decimal("8.0"),
            units_to_add=Decimal("1.5")
        )
        scale3 = CorrectionScale.objects.create(
            greater_than=Decimal("12.0"),
            units_to_add=Decimal("3.0")
        )
        
        scales = list(CorrectionScale.objects.all())
        
        assert scales[0] == scale2  # 8.0
        assert scales[1] == scale1  # 10.0
        assert scales[2] == scale3  # 12.0

    def test_correction_scale_decimal_precision(self):
        """Test that decimal fields maintain precision."""
        scale = CorrectionScale.objects.create(
            greater_than=Decimal("8.5"),
            units_to_add=Decimal("2.25")
        )
        
        scale.refresh_from_db()
        
        assert scale.greater_than == Decimal("8.5")
        assert scale.units_to_add == Decimal("2.25")

    def test_correction_scale_timestamps(self):
        """Test that timestamps are automatically set."""
        scale = CorrectionScale.objects.create(
            greater_than=Decimal("9.0"),
            units_to_add=Decimal("2.0")
        )
        
        assert scale.created_at is not None
        assert scale.updated_at is not None
        # Allow for small time difference due to database precision
        time_diff = abs((scale.updated_at - scale.created_at).total_seconds())
        assert time_diff < 1  # Should be within 1 second
        
        # Update and check that updated_at changes
        import time
        time.sleep(0.01)  # Small delay to ensure updated_at is different
        scale.units_to_add = Decimal("2.5")
        scale.save()
        scale.refresh_from_db()
        
        assert scale.updated_at > scale.created_at
