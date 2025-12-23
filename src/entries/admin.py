from django.contrib import admin
from .models import (
    CorrectionScale,
    GlucoseReading,
    InsulinDose,
    InsulinSchedule,
    InsulinType,
    Meal,
)


@admin.register(InsulinType)
class InsulinTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "last_modified_by", "notes", "is_default"]
    list_filter = ["type", "is_default"]
    search_fields = ["name", "notes"]
    autocomplete_fields = ["last_modified_by"]


@admin.register(GlucoseReading)
class GlucoseReadingAdmin(admin.ModelAdmin):
    list_display = ["last_modified_by", "occurred_at", "value", "unit"]
    list_filter = ["unit", "occurred_at"]
    search_fields = ["last_modified_by__email", "notes"]
    date_hierarchy = "occurred_at"
    ordering = ["-occurred_at"]
    autocomplete_fields = ["last_modified_by"]


@admin.register(InsulinDose)
class InsulinDoseAdmin(admin.ModelAdmin):
    list_display = [
        "last_modified_by",
        "occurred_at",
        "base_units",
        "correction_units",
        "total_units",
        "insulin_type",
    ]
    list_filter = ["insulin_type", "occurred_at"]
    search_fields = ["last_modified_by__email", "notes", "insulin_type__name"]
    date_hierarchy = "occurred_at"
    ordering = ["-occurred_at"]
    autocomplete_fields = ["last_modified_by", "insulin_type"]

    def total_units(self, obj):
        """Calculate and display total units."""
        return obj.base_units + obj.correction_units

    total_units.short_description = "Total Units"


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = [
        "last_modified_by",
        "occurred_at",
        "meal_type",
        "total_carbs",
    ]
    list_filter = ["meal_type", "occurred_at"]
    search_fields = ["last_modified_by__email", "description", "notes"]
    date_hierarchy = "occurred_at"
    ordering = ["-occurred_at"]
    autocomplete_fields = ["last_modified_by"]


@admin.register(CorrectionScale)
class CorrectionScaleAdmin(admin.ModelAdmin):
    list_display = ["greater_than", "units_to_add", "created_at", "updated_at"]
    ordering = ["greater_than"]
    search_fields = ["greater_than", "units_to_add"]


@admin.register(InsulinSchedule)
class InsulinScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "label",
        "time",
        "insulin_type",
        "units",
        "last_modified_by",
        "created_at",
    ]
    list_filter = ["insulin_type", "time"]
    search_fields = ["label", "insulin_type__name", "notes", "last_modified_by__email"]
    ordering = ["time"]
    autocomplete_fields = ["insulin_type", "last_modified_by"]
