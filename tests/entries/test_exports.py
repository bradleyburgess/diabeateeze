"""Tests for export functionality."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from entries.exports import (
    GlucoseReadingExporter,
    InsulinDoseExporter,
    MealExporter,
    get_exporter_for_model,
)
from entries.models import GlucoseReading, InsulinDose, InsulinType, Meal


@pytest.mark.django_db
class TestGlucoseReadingExporter:
    """Tests for GlucoseReadingExporter."""

    def test_get_headers(self, user):
        """Test that headers are correct."""
        reading = GlucoseReading.objects.create(
            last_modified_by=user,
            occurred_at=timezone.now(),
            value=Decimal("7.5"),
            unit="mmol/L",
        )
        exporter = GlucoseReadingExporter(GlucoseReading.objects.all(), GlucoseReading)
        headers = exporter.get_headers()
        assert headers == ["Date", "Time", "Value", "Unit", "Notes"]

    def test_get_row_data(self, user):
        """Test that row data is formatted correctly."""
        occurred_at = timezone.now()
        reading = GlucoseReading.objects.create(
            last_modified_by=user,
            occurred_at=occurred_at,
            value=Decimal("7.5"),
            unit="mmol/L",
            notes="Test note",
        )
        exporter = GlucoseReadingExporter(GlucoseReading.objects.all(), GlucoseReading)
        row_data = exporter.get_row_data(reading)
        assert row_data[0] == occurred_at.strftime("%Y-%m-%d")
        assert row_data[1] == occurred_at.strftime("%H:%M:%S")
        assert row_data[2] == 7.5
        assert row_data[3] == "mmol/L"
        assert row_data[4] == "Test note"

    def test_format_text_entry(self, user):
        """Test text formatting for glucose readings."""
        occurred_at = timezone.now()
        reading = GlucoseReading.objects.create(
            last_modified_by=user,
            occurred_at=occurred_at,
            value=Decimal("7.5"),
            unit="mmol/L",
            notes="Test note",
        )
        exporter = GlucoseReadingExporter(GlucoseReading.objects.all(), GlucoseReading)
        text = exporter.format_text_entry(reading)
        # New format is: "- 2025/12/24 7:46 am: 7.5 mmol/L"
        assert text.startswith("- ")
        assert "7.5 mmol/L" in text

    def test_to_csv(self, user):
        """Test CSV export."""
        reading = GlucoseReading.objects.create(
            last_modified_by=user,
            occurred_at=timezone.now(),
            value=Decimal("7.5"),
            unit="mmol/L",
        )
        exporter = GlucoseReadingExporter(GlucoseReading.objects.all(), GlucoseReading)
        response = exporter.to_csv()
        assert response["Content-Type"] == "text/csv"
        assert "glucosereading" in response["Content-Disposition"]
        content = response.content.decode("utf-8")
        assert "Date,Time,Value,Unit,Notes" in content

    def test_to_excel(self, user):
        """Test Excel export."""
        reading = GlucoseReading.objects.create(
            last_modified_by=user,
            occurred_at=timezone.now(),
            value=Decimal("7.5"),
            unit="mmol/L",
        )
        exporter = GlucoseReadingExporter(GlucoseReading.objects.all(), GlucoseReading)
        response = exporter.to_excel()
        assert "spreadsheet" in response["Content-Type"]
        assert "glucosereading" in response["Content-Disposition"]
        assert response.content  # Should have content

    def test_to_text(self, user):
        """Test text export."""
        reading = GlucoseReading.objects.create(
            last_modified_by=user,
            occurred_at=timezone.now(),
            value=Decimal("7.5"),
            unit="mmol/L",
            notes="Test note",
        )
        exporter = GlucoseReadingExporter(GlucoseReading.objects.all(), GlucoseReading)
        response = exporter.to_text()
        assert response["Content-Type"] == "text/plain; charset=utf-8"
        assert "glucosereading" in response["Content-Disposition"]
        content = response.content.decode("utf-8")
        assert "Glucose Reading" in content
        assert "7.5 mmol/L" in content


@pytest.mark.django_db
class TestInsulinDoseExporter:
    """Tests for InsulinDoseExporter."""

    def test_get_row_data(self, user):
        """Test that row data is formatted correctly."""
        insulin_type = InsulinType.objects.create(
            name="Test Insulin",
            type=InsulinType.Type.RAPID_ACTING,
        )
        occurred_at = timezone.now()
        dose = InsulinDose.objects.create(
            last_modified_by=user,
            occurred_at=occurred_at,
            base_units=Decimal("10.0"),
            correction_units=Decimal("2.5"),
            insulin_type=insulin_type,
            notes="Test dose",
        )
        exporter = InsulinDoseExporter(InsulinDose.objects.all(), InsulinDose)
        row_data = exporter.get_row_data(dose)
        assert row_data[2] == "Test Insulin"
        assert row_data[3] == 10.0
        assert row_data[4] == 2.5
        assert row_data[5] == 12.5  # Total

    def test_format_text_entry(self, user):
        """Test text formatting for insulin doses."""
        insulin_type = InsulinType.objects.create(
            name="Test Insulin",
            type=InsulinType.Type.RAPID_ACTING,
        )
        dose = InsulinDose.objects.create(
            last_modified_by=user,
            occurred_at=timezone.now(),
            base_units=Decimal("10.0"),
            correction_units=Decimal("2.5"),
            insulin_type=insulin_type,
        )
        exporter = InsulinDoseExporter(InsulinDose.objects.all(), InsulinDose)
        text = exporter.format_text_entry(dose)
        assert "Insulin Dose" in text
        assert "Test Insulin" in text
        assert "Base: 10.0 units" in text
        assert "Correction: 2.5 units" in text
        assert "Total: 12.5 units" in text


@pytest.mark.django_db
class TestMealExporter:
    """Tests for MealExporter."""

    def test_get_row_data(self, user):
        """Test that row data is formatted correctly."""
        occurred_at = timezone.now()
        meal = Meal.objects.create(
            last_modified_by=user,
            occurred_at=occurred_at,
            meal_type="breakfast",
            description="Oatmeal with berries",
            total_carbs=Decimal("45.5"),
            notes="Delicious",
        )
        exporter = MealExporter(Meal.objects.all(), Meal)
        row_data = exporter.get_row_data(meal)
        assert row_data[2] == "Breakfast"
        assert row_data[3] == "Oatmeal with berries"
        assert row_data[4] == 45.5
        assert row_data[5] == "Delicious"

    def test_format_text_entry(self, user):
        """Test text formatting for meals."""
        meal = Meal.objects.create(
            last_modified_by=user,
            occurred_at=timezone.now(),
            meal_type="lunch",
            description="Sandwich",
            total_carbs=Decimal("30.0"),
        )
        exporter = MealExporter(Meal.objects.all(), Meal)
        text = exporter.format_text_entry(meal)
        assert "Lunch" in text
        assert "Sandwich" in text
        assert "30.0g" in text


@pytest.mark.django_db
class TestExporterFactory:
    """Tests for get_exporter_for_model factory function."""

    def test_get_exporter_for_model(self):
        """Test that factory returns correct exporter classes."""
        assert get_exporter_for_model(GlucoseReading) == GlucoseReadingExporter
        assert get_exporter_for_model(InsulinDose) == InsulinDoseExporter
        assert get_exporter_for_model(Meal) == MealExporter
