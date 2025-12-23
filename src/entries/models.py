from django.conf import settings
from django.db import models

from base.mixins import AutoLastModifiedMixin
from base.models import TimestampedModel, UUIDModel


class InsulinType(AutoLastModifiedMixin, TimestampedModel):
    """Insulin type classification."""

    class Type(models.TextChoices):
        RAPID_ACTING = "rapid", "Rapid-Acting"
        SHORT_ACTING = "short", "Short-Acting"
        INTERMEDIATE_ACTING = "intermediate", "Intermediate-Acting"
        LONG_ACTING = "long", "Long-Acting"
        ULTRA_LONG_ACTING = "ultra_long", "Ultra Long-Acting"
        PREMIXED = "premixed", "Premixed"

    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_insulin_types",
    )
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.RAPID_ACTING,
    )
    notes = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:  # type: ignore[misc]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Ensure only one InsulinType can be marked as default."""
        if self.is_default:
            # Set all other instances to is_default=False
            InsulinType.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class GlucoseReading(AutoLastModifiedMixin, TimestampedModel):
    """Blood glucose reading."""

    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="glucose_readings",
    )
    occurred_at = models.DateTimeField()
    value = models.DecimalField(max_digits=5, decimal_places=1)
    unit = models.CharField(
        max_length=10,
        choices=[("mmol/L", "mmol/L"), ("mg/dL", "mg/dL")],
        default="mmol/L",
    )
    notes = models.TextField(blank=True)

    class Meta:  # type: ignore[misc]
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["last_modified_by", "-occurred_at"])]

    def __str__(self):
        return f"{self.value} {self.unit} at {self.occurred_at}"


class InsulinDose(AutoLastModifiedMixin, TimestampedModel):
    """Insulin dose administration."""

    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="insulin_doses",
    )
    occurred_at = models.DateTimeField()
    base_units = models.DecimalField(max_digits=5, decimal_places=2)
    correction_units = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    insulin_type = models.ForeignKey(
        "InsulinType",
        on_delete=models.PROTECT,
        related_name="doses",
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:  # type: ignore[misc]
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["last_modified_by", "-occurred_at"])]

    def __str__(self):
        total = self.base_units + self.correction_units
        return f"{total} units ({self.base_units} base + {self.correction_units} correction) of {self.insulin_type.name} at {self.occurred_at}"


class Meal(AutoLastModifiedMixin, TimestampedModel):
    """Meal or snack entry."""

    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="meals",
    )
    occurred_at = models.DateTimeField()
    meal_type = models.CharField(
        max_length=20,
        choices=[
            ("breakfast", "Breakfast"),
            ("lunch", "Lunch"),
            ("dinner", "Dinner"),
            ("snack", "Snack"),
        ],
    )
    description = models.TextField()
    total_carbs = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Total carbohydrates in grams",
    )
    notes = models.TextField(blank=True)

    class Meta:  # type: ignore[misc]
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["last_modified_by", "-occurred_at"])]

    def __str__(self):
        return f"{self.get_meal_type_display()} at {self.occurred_at}"  # type: ignore[misc]


class InsulinSchedule(AutoLastModifiedMixin, TimestampedModel):
    """Scheduled insulin dose times."""

    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_insulin_schedules",
    )
    label = models.CharField(max_length=100, help_text="Label for this scheduled dose")
    time = models.TimeField(help_text="Scheduled time for this dose")
    insulin_type = models.ForeignKey(
        "InsulinType",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    units = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Scheduled units of insulin",
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:  # type: ignore[misc]
        ordering = ["time"]

    def __str__(self):
        return f"{self.label} at {self.time.strftime('%H:%M')}"


class CorrectionScale(TimestampedModel):
    """Correction scale for insulin dosing based on glucose levels."""

    greater_than = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        help_text="Blood glucose threshold (e.g., 8.0 mmol/L)",
    )
    units_to_add = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Units of insulin to add when above threshold",
    )

    class Meta:  # type: ignore[misc]
        ordering = ["greater_than"]

    def __str__(self):
        return f"Above {self.greater_than}: +{self.units_to_add} units"
