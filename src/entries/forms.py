from django import forms

from .models import (
    CorrectionScale,
    GlucoseReading,
    InsulinDose,
    InsulinSchedule,
    InsulinType,
    Meal,
)


class GlucoseReadingForm(forms.ModelForm):
    """Form for creating/editing glucose readings."""

    class Meta:
        model = GlucoseReading
        fields = ["occurred_at", "value", "unit", "notes"]
        widgets = {
            "occurred_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),
            "value": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "placeholder": "e.g., 5.5",
                }
            ),
            "unit": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional notes about this reading...",
                }
            ),
        }
        labels = {
            "occurred_at": "Date & Time",
            "value": "Blood Glucose Value",
            "unit": "Unit",
            "notes": "Notes",
        }


class MealForm(forms.ModelForm):
    """Form for creating/editing meals."""

    class Meta:
        model = Meal
        fields = ["occurred_at", "meal_type", "description", "total_carbs", "notes"]
        widgets = {
            "occurred_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),
            "meal_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe what you ate...",
                }
            ),
            "total_carbs": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "placeholder": "e.g., 45.0",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional additional notes...",
                }
            ),
        }
        labels = {
            "occurred_at": "Date & Time",
            "meal_type": "Meal Type",
            "description": "Description",
            "total_carbs": "Total Carbohydrates (g)",
            "notes": "Notes",
        }


class InsulinDoseForm(forms.ModelForm):
    """Form for creating/editing insulin doses."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default insulin type when creating a new dose (not editing)
        if self.instance._state.adding and "insulin_type" not in self.initial:
            default_type = InsulinType.objects.filter(is_default=True).first()
            if default_type:
                self.fields["insulin_type"].initial = default_type

    class Meta:
        model = InsulinDose
        fields = [
            "occurred_at",
            "base_units",
            "correction_units",
            "insulin_type",
            "notes",
        ]
        widgets = {
            "occurred_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),
            "base_units": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "e.g., 10.0",
                }
            ),
            "correction_units": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "e.g., 2.5",
                }
            ),
            "insulin_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional notes about this dose...",
                }
            ),
        }
        labels = {
            "occurred_at": "Date & Time",
            "base_units": "Base Units",
            "correction_units": "Correction Units",
            "insulin_type": "Insulin Type",
            "notes": "Notes",
        }

    def clean_notes(self):
        """Convert empty string to None for notes."""
        notes = self.cleaned_data.get("notes")
        return notes if notes else None


class InsulinScheduleForm(forms.ModelForm):
    """Form for creating/editing insulin schedules."""

    class Meta:
        model = InsulinSchedule
        fields = ["label", "time", "insulin_type", "units", "notes"]
        widgets = {
            "label": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Morning dose, Before breakfast",
                }
            ),
            "time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),
            "insulin_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "units": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "e.g., 10.5",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional notes about this scheduled dose...",
                }
            ),
        }
        labels = {
            "label": "Label",
            "time": "Time",
            "insulin_type": "Insulin Type",
            "units": "Units",
            "notes": "Notes",
        }

    def clean_notes(self):
        """Convert empty string to None for notes."""
        notes = self.cleaned_data.get("notes")
        return notes if notes else None


class CorrectionScaleForm(forms.ModelForm):
    """Form for creating/editing correction scale entries."""

    class Meta:
        model = CorrectionScale
        fields = ["greater_than", "units_to_add"]
        widgets = {
            "greater_than": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "placeholder": "e.g., 8.0",
                }
            ),
            "units_to_add": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "e.g., 2.0",
                }
            ),
        }
        labels = {
            "greater_than": "Blood Glucose Greater Than",
            "units_to_add": "Units to Add",
        }
