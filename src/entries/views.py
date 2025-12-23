from datetime import datetime, timedelta
from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    CorrectionScaleForm,
    GlucoseReadingForm,
    InsulinDoseForm,
    InsulinScheduleForm,
    MealForm,
)
from .models import CorrectionScale, GlucoseReading, InsulinDose, InsulinSchedule, Meal


@login_required
def quick_add(request):
    """Quick access page for adding readings."""
    return render(request, "entries/quick_add.html")


@login_required
def activity(request):
    """Display all activity (readings, doses, meals) in chronological order."""
    # Get date filter parameters
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    filter_type = request.GET.get("filter")  # 'today' or 'yesterday'

    # Initialize date range
    start_datetime = None
    end_datetime = None

    # Handle quick filters
    if filter_type == "today":
        today = timezone.now().date()
        start_datetime = timezone.make_aware(
            datetime.combine(today, datetime.min.time())
        )
        end_datetime = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    elif filter_type == "yesterday":
        yesterday = timezone.now().date() - timedelta(days=1)
        start_datetime = timezone.make_aware(
            datetime.combine(yesterday, datetime.min.time())
        )
        end_datetime = timezone.make_aware(
            datetime.combine(yesterday, datetime.max.time())
        )
    elif start_date or end_date:
        # Handle custom date range
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            start_datetime = timezone.make_aware(
                datetime.combine(start_dt.date(), datetime.min.time())
            )
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_datetime = timezone.make_aware(
                datetime.combine(end_dt.date(), datetime.max.time())
            )

    # Query all three types of entries
    glucose_readings = GlucoseReading.objects.select_related("last_modified_by")
    insulin_doses = InsulinDose.objects.select_related(
        "last_modified_by", "insulin_type"
    )
    meals = Meal.objects.select_related("last_modified_by")

    # Apply date filters if specified
    if start_datetime:
        glucose_readings = glucose_readings.filter(occurred_at__gte=start_datetime)
        insulin_doses = insulin_doses.filter(occurred_at__gte=start_datetime)
        meals = meals.filter(occurred_at__gte=start_datetime)

    if end_datetime:
        glucose_readings = glucose_readings.filter(occurred_at__lte=end_datetime)
        insulin_doses = insulin_doses.filter(occurred_at__lte=end_datetime)
        meals = meals.filter(occurred_at__lte=end_datetime)

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
    )

    # Paginate the combined results
    page_size = request.GET.get("page_size", "50")
    try:
        page_size = int(page_size)
        if page_size not in [10, 25, 50, 100]:
            page_size = 50
    except (ValueError, TypeError):
        page_size = 50

    paginator = Paginator(all_entries, page_size)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "page_size": page_size,
        "start_date": start_date or "",
        "end_date": end_date or "",
        "filter_type": filter_type or "",
    }

    return render(request, "entries/activity.html", context)


@login_required
def glucose_readings_list(request):
    """Display paginated list of glucose readings."""
    # Get page size from query parameter, default to 50
    page_size = request.GET.get("page_size", "50")
    try:
        page_size = int(page_size)
        # Limit page size to reasonable values
        if page_size not in [10, 25, 50, 100]:
            page_size = 50
    except (ValueError, TypeError):
        page_size = 50

    # Get all readings ordered by most recent first
    readings = GlucoseReading.objects.select_related("last_modified_by").order_by(
        "-occurred_at"
    )

    # Paginate
    paginator = Paginator(readings, page_size)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "page_size": page_size,
    }

    return render(request, "entries/glucose_readings_list.html", context)


@login_required
def glucose_reading_create(request):
    """Create a new glucose reading."""
    if request.method == "POST":
        form = GlucoseReadingForm(request.POST)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.last_modified_by = request.user
            reading.save()
            messages.success(request, "Blood glucose reading added successfully!")
            return redirect("entries:glucose_readings_list")
    else:
        form = GlucoseReadingForm()

    return render(
        request,
        "entries/glucose_reading_form.html",
        {
            "form": form,
            "title": "Add Blood Glucose Reading",
        },
    )


@login_required
def glucose_reading_edit(request, pk):
    """Edit an existing glucose reading."""
    reading = GlucoseReading.objects.filter(
        pk=pk, last_modified_by=request.user
    ).first()

    if not reading:
        messages.error(
            request, "Reading not found or you don't have permission to edit it."
        )
        return redirect("entries:glucose_readings_list")

    if request.method == "POST":
        form = GlucoseReadingForm(request.POST, instance=reading)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.last_modified_by = request.user
            reading.save()
            messages.success(request, "Blood glucose reading updated successfully!")
            return redirect("entries:glucose_readings_list")
    else:
        form = GlucoseReadingForm(instance=reading)

    return render(
        request,
        "entries/glucose_reading_form.html",
        {
            "form": form,
            "title": "Edit Blood Glucose Reading",
            "reading": reading,
        },
    )


@login_required
def meals_list(request):
    """Display paginated list of meals."""
    # Get page size from query parameter, default to 50
    page_size = request.GET.get("page_size", "50")
    try:
        page_size = int(page_size)
        # Limit page size to reasonable values
        if page_size not in [10, 25, 50, 100]:
            page_size = 50
    except (ValueError, TypeError):
        page_size = 50

    # Get all meals ordered by most recent first
    meals = Meal.objects.select_related("last_modified_by").order_by("-occurred_at")

    # Paginate
    paginator = Paginator(meals, page_size)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "page_size": page_size,
    }

    return render(request, "entries/meals_list.html", context)


@login_required
def meal_create(request):
    """Create a new meal."""
    if request.method == "POST":
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.last_modified_by = request.user
            meal.save()
            messages.success(request, "Meal added successfully!")
            return redirect("entries:meals_list")
    else:
        form = MealForm()

    return render(
        request,
        "entries/meal_form.html",
        {
            "form": form,
            "title": "Add Meal",
        },
    )


@login_required
def meal_edit(request, pk):
    """Edit an existing meal."""
    meal = Meal.objects.filter(pk=pk, last_modified_by=request.user).first()

    if not meal:
        messages.error(
            request, "Meal not found or you don't have permission to edit it."
        )
        return redirect("entries:meals_list")

    if request.method == "POST":
        form = MealForm(request.POST, instance=meal)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.last_modified_by = request.user
            meal.save()
            messages.success(request, "Meal updated successfully!")
            return redirect("entries:meals_list")
    else:
        form = MealForm(instance=meal)

    return render(
        request,
        "entries/meal_form.html",
        {
            "form": form,
            "title": "Edit Meal",
            "meal": meal,
        },
    )


@login_required
def insulin_doses_list(request):
    """Display paginated list of insulin doses."""
    # Get page size from query parameter, default to 50
    page_size = request.GET.get("page_size", "50")
    try:
        page_size = int(page_size)
        # Limit page size to reasonable values
        if page_size not in [10, 25, 50, 100]:
            page_size = 50
    except (ValueError, TypeError):
        page_size = 50

    # Get all doses ordered by most recent first
    doses = InsulinDose.objects.select_related(
        "last_modified_by", "insulin_type"
    ).order_by("-occurred_at")

    # Paginate
    paginator = Paginator(doses, page_size)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "page_size": page_size,
    }

    return render(request, "entries/insulin_doses_list.html", context)


@login_required
def insulin_dose_create(request):
    """Create a new insulin dose."""
    if request.method == "POST":
        form = InsulinDoseForm(request.POST)
        if form.is_valid():
            dose = form.save(commit=False)
            dose.last_modified_by = request.user
            dose.save()
            messages.success(request, "Insulin dose added successfully!")
            return redirect("entries:insulin_doses_list")
    else:
        form = InsulinDoseForm()

    return render(
        request,
        "entries/insulin_dose_form.html",
        {
            "form": form,
            "title": "Add Insulin Dose",
        },
    )


@login_required
def insulin_dose_edit(request, pk):
    """Edit an existing insulin dose."""
    dose = get_object_or_404(InsulinDose, pk=pk, last_modified_by=request.user)

    if request.method == "POST":
        form = InsulinDoseForm(request.POST, instance=dose)
        if form.is_valid():
            dose = form.save(commit=False)
            dose.last_modified_by = request.user
            dose.save()
            messages.success(request, "Insulin dose updated successfully!")
            return redirect("entries:insulin_doses_list")
    else:
        form = InsulinDoseForm(instance=dose)

    return render(
        request,
        "entries/insulin_dose_form.html",
        {
            "form": form,
            "title": "Edit Insulin Dose",
            "dose": dose,
        },
    )


@login_required
def insulin_schedules_list(request):
    """Display list of insulin schedules."""
    schedules = InsulinSchedule.objects.select_related("insulin_type").order_by("time")

    context = {
        "schedules": schedules,
    }

    return render(request, "entries/insulin_schedules_list.html", context)


@login_required
def insulin_schedule_create(request):
    """Create a new insulin schedule."""
    if request.method == "POST":
        form = InsulinScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, "Insulin schedule added successfully!")
            return redirect("entries:insulin_schedules_list")
    else:
        form = InsulinScheduleForm()

    return render(
        request,
        "entries/insulin_schedule_form.html",
        {
            "form": form,
            "title": "Add Insulin Schedule",
        },
    )


@login_required
def insulin_schedule_edit(request, pk):
    """Edit an existing insulin schedule."""
    schedule = get_object_or_404(InsulinSchedule, pk=pk)

    if request.method == "POST":
        form = InsulinScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, "Insulin schedule updated successfully!")
            return redirect("entries:insulin_schedules_list")
    else:
        form = InsulinScheduleForm(instance=schedule)

    return render(
        request,
        "entries/insulin_schedule_form.html",
        {
            "form": form,
            "title": "Edit Insulin Schedule",
            "schedule": schedule,
        },
    )


@login_required
def correction_scales_list(request):
    """Display paginated list of correction scales."""
    # Get page size from query parameter, default to 50
    page_size = request.GET.get("page_size", "50")
    try:
        page_size = int(page_size)
        # Limit page size to reasonable values
        if page_size not in [10, 25, 50, 100]:
            page_size = 50
    except (ValueError, TypeError):
        page_size = 50

    # Get all correction scales ordered by threshold
    scales = CorrectionScale.objects.all().order_by("greater_than")

    # Paginate
    paginator = Paginator(scales, page_size)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "page_size": page_size,
    }

    return render(request, "entries/correction_scales_list.html", context)


@login_required
def correction_scale_create(request):
    """Create a new correction scale entry."""
    if request.method == "POST":
        form = CorrectionScaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Correction scale entry added successfully!")
            return redirect("entries:correction_scales_list")
    else:
        form = CorrectionScaleForm()

    return render(
        request,
        "entries/correction_scale_form.html",
        {
            "form": form,
            "title": "Add Correction Scale",
        },
    )


@login_required
def correction_scale_edit(request, pk):
    """Edit an existing correction scale entry."""
    scale = get_object_or_404(CorrectionScale, pk=pk)

    if request.method == "POST":
        form = CorrectionScaleForm(request.POST, instance=scale)
        if form.is_valid():
            form.save()
            messages.success(request, "Correction scale entry updated successfully!")
            return redirect("entries:correction_scales_list")
    else:
        form = CorrectionScaleForm(instance=scale)

    return render(
        request,
        "entries/correction_scale_form.html",
        {
            "form": form,
            "title": "Edit Correction Scale",
            "scale": scale,
        },
    )
