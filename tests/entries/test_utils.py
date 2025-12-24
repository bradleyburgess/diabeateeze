"""Tests for entries utilities."""
import pytest
from datetime import datetime
from django.test import RequestFactory
from django.utils import timezone

from entries.utils import get_date_filters


@pytest.mark.django_db
class TestGetDateFilters:
    """Tests for get_date_filters utility function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()

    def test_no_filters(self):
        """Test with no filter parameters."""
        request = self.factory.get("/")
        result = get_date_filters(request)
        
        assert result["start_datetime"] is None
        assert result["end_datetime"] is None
        assert result["start_date"] == ""
        assert result["end_date"] == ""

    def test_today_filter(self):
        """Test filtering for today using date range."""
        today = timezone.now().date().strftime("%Y-%m-%d")
        request = self.factory.get("/", {
            "start_date": today,
            "end_date": today
        })
        result = get_date_filters(request)
        
        today_date = timezone.now().date()
        assert result["start_datetime"].date() == today_date
        assert result["end_datetime"].date() == today_date

    def test_two_days_filter(self):
        """Test filtering for yesterday and today using date range."""
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        
        request = self.factory.get("/", {
            "start_date": yesterday.strftime("%Y-%m-%d"),
            "end_date": today.strftime("%Y-%m-%d")
        })
        result = get_date_filters(request)
        
        assert result["start_datetime"].date() == yesterday
        assert result["end_datetime"].date() == today

    def test_custom_date_range(self):
        """Test custom date range filter."""
        request = self.factory.get("/", {
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        })
        result = get_date_filters(request)
        
        assert result["start_datetime"].date() == datetime(2023, 1, 1).date()
        assert result["end_datetime"].date() == datetime(2023, 1, 31).date()
        assert result["start_date"] == "2023-01-01"
        assert result["end_date"] == "2023-01-31"

    def test_start_date_only(self):
        """Test with only start date."""
        request = self.factory.get("/", {"start_date": "2023-06-15"})
        result = get_date_filters(request)
        
        assert result["start_datetime"].date() == datetime(2023, 6, 15).date()
        assert result["end_datetime"] is None
        assert result["start_date"] == "2023-06-15"
        assert result["end_date"] == ""

    def test_end_date_only(self):
        """Test with only end date."""
        request = self.factory.get("/", {"end_date": "2023-12-31"})
        result = get_date_filters(request)
        
        assert result["start_datetime"] is None
        assert result["end_datetime"].date() == datetime(2023, 12, 31).date()
        assert result["start_date"] == ""
        assert result["end_date"] == "2023-12-31"
