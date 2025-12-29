import json
import statistics
from datetime import timedelta
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

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
    now = timezone.now()
    one_week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)
    
    # Get glucose statistics for the past week
    weekly_readings = GlucoseReading.objects.filter(
        occurred_at__gte=one_week_ago
    ).order_by('occurred_at')
    
    glucose_stats = {
        'highest': None,
        'lowest': None,
        'median': None,
    }
    
    if weekly_readings.exists():
        values = [float(r.value) for r in weekly_readings]
        glucose_stats['highest'] = max(values)
        glucose_stats['lowest'] = min(values)
        glucose_stats['median'] = statistics.median(values)
    
    # Get daily averages for the past two weeks
    two_week_readings = GlucoseReading.objects.filter(
        occurred_at__gte=two_weeks_ago
    ).order_by('occurred_at')
    
    daily_averages = {}
    for reading in two_week_readings:
        date_key = reading.occurred_at.date().isoformat()
        if date_key not in daily_averages:
            daily_averages[date_key] = []
        daily_averages[date_key].append(float(reading.value))
    
    daily_avg_data = [
        {
            "date": date,
            "average": sum(values) / len(values)
        }
        for date, values in sorted(daily_averages.items())
    ]
    
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
        "glucose_stats": glucose_stats,
        "daily_avg_data": json.dumps(daily_avg_data),
        "has_glucose_data": two_week_readings.exists(),
    }

    return render(request, "dashboard/dashboard.html", context)
