from itertools import chain

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from entries.models import (
    CorrectionScale,
    GlucoseReading,
    InsulinDose,
    InsulinSchedule,
    Meal,
)


@login_required
def dashboard_view(request):
    """Dashboard view - requires authentication."""
    # Get recent activity (last 10 entries)
    glucose_readings = GlucoseReading.objects.select_related("last_modified_by")[:10]
    insulin_doses = InsulinDose.objects.select_related(
        "last_modified_by", "insulin_type"
    )[:10]
    meals = Meal.objects.select_related("last_modified_by")[:10]

    # Add a type attribute to each entry for template rendering
    for reading in glucose_readings:
        reading.entry_type = "glucose"
    for dose in insulin_doses:
        dose.entry_type = "insulin"
    for meal in meals:
        meal.entry_type = "meal"

    # Combine all entries and sort by occurred_at (newest first)
    all_entries = sorted(
        chain(glucose_readings, insulin_doses, meals),
        key=lambda x: x.occurred_at,
        reverse=True,
    )[:10]

    # Get insulin schedules and correction scales
    insulin_schedules = InsulinSchedule.objects.select_related("insulin_type").all()
    correction_scales = CorrectionScale.objects.all()

    context = {
        "recent_entries": all_entries,
        "insulin_schedules": insulin_schedules,
        "correction_scales": correction_scales,
    }

    return render(request, "dashboard/dashboard.html", context)
