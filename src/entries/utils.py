"""Utility functions for entries app."""
from datetime import datetime, timedelta
from django.utils import timezone


def get_date_filters(request):
    """
    Extract and process date filter parameters from request.
    
    Returns a dictionary containing:
    - start_datetime: timezone-aware datetime for start of range (or None)
    - end_datetime: timezone-aware datetime for end of range (or None)
    - start_date: string representation of start date for template (or "")
    - end_date: string representation of end date for template (or "")
    - filter_type: quick filter type ('today', 'yesterday', or "")
    """
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

    return {
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "start_date": start_date or "",
        "end_date": end_date or "",
        "filter_type": filter_type or "",
    }
