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
        assert result["filter_type"] == ""

    def test_today_filter(self):
        """Test today quick filter."""
        request = self.factory.get("/", {"filter": "today"})
        result = get_date_filters(request)
        
        today = timezone.now().date()
        assert result["start_datetime"].date() == today
        assert result["end_datetime"].date() == today
        assert result["filter_type"] == "today"

    def test_yesterday_filter(self):
        """Test yesterday quick filter."""
        request = self.factory.get("/", {"filter": "yesterday"})
        result = get_date_filters(request)
        
        yesterday = timezone.now().date()
        from datetime import timedelta
        yesterday = yesterday - timedelta(days=1)
        
        assert result["start_datetime"].date() == yesterday
        assert result["end_datetime"].date() == yesterday
        assert result["filter_type"] == "yesterday"

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
        assert result["filter_type"] == ""

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

    def test_quick_filter_overrides_custom_dates(self):
        """Test that quick filters take precedence over custom dates."""
        request = self.factory.get("/", {
            "filter": "today",
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        })
        result = get_date_filters(request)
        
        # Should use today, not the custom dates
        today = timezone.now().date()
        assert result["start_datetime"].date() == today
        assert result["end_datetime"].date() == today
        assert result["filter_type"] == "today"
