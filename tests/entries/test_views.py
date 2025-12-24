"""Tests for entries views."""
import pytest
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone

from entries.models import CorrectionScale, GlucoseReading, Meal, InsulinDose, InsulinType


@pytest.mark.django_db
class TestGlucoseReadingsListView:
    """Tests for glucose_readings_list view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:glucose_readings_list"))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_view_with_authenticated_user(self, client, user):
        """Test that authenticated users can access the view."""
        client.force_login(user)
        response = client.get(reverse("entries:glucose_readings_list"))
        assert response.status_code == 200
        assert "entries/glucose_readings_list.html" in [t.name for t in response.templates]

    def test_pagination_default_page_size(self, client, user):
        """Test that default page size is 50."""
        client.force_login(user)
        
        # Create 75 readings
        for i in range(75):
            GlucoseReading.objects.create(
                occurred_at=timezone.now() - timezone.timedelta(hours=i),
                value=Decimal("5.5"),
                unit="mmol/L",
                last_modified_by=user
            )
        
        response = client.get(reverse("entries:glucose_readings_list"))
        assert response.status_code == 200
        assert len(response.context["page_obj"]) == 50
        assert response.context["page_size"] == 50

    def test_pagination_custom_page_size(self, client, user):
        """Test custom page sizes."""
        client.force_login(user)
        
        # Create 30 readings
        for i in range(30):
            GlucoseReading.objects.create(
                occurred_at=timezone.now() - timezone.timedelta(hours=i),
                value=Decimal("5.5"),
                unit="mmol/L",
                last_modified_by=user
            )
        
        for page_size in [10, 25, 50, 100]:
            response = client.get(
                reverse("entries:glucose_readings_list"),
                {"page_size": page_size}
            )
            assert response.status_code == 200
            expected_items = min(page_size, 30)
            assert len(response.context["page_obj"]) == expected_items
            assert response.context["page_size"] == page_size

    def test_invalid_page_size_defaults_to_50(self, client, user):
        """Test that invalid page size defaults to 50."""
        client.force_login(user)
        
        # Test with invalid page size
        response = client.get(
            reverse("entries:glucose_readings_list"),
            {"page_size": "invalid"}
        )
        assert response.status_code == 200
        assert response.context["page_size"] == 50

    def test_readings_ordered_by_most_recent(self, client, user):
        """Test that readings are ordered by most recent first."""
        client.force_login(user)
        
        # Create readings with specific times
        older_reading = GlucoseReading.objects.create(
            occurred_at=timezone.now() - timezone.timedelta(hours=2),
            value=Decimal("5.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        newer_reading = GlucoseReading.objects.create(
            occurred_at=timezone.now() - timezone.timedelta(hours=1),
            value=Decimal("6.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:glucose_readings_list"))
        readings = list(response.context["page_obj"])
        
        # Newer reading should be first
        assert readings[0].id == newer_reading.id
        assert readings[1].id == older_reading.id

    def test_empty_readings_list(self, client, user):
        """Test view with no readings."""
        client.force_login(user)
        response = client.get(reverse("entries:glucose_readings_list"))
        assert response.status_code == 200
        assert len(response.context["page_obj"]) == 0

    def test_filter_today(self, client, user):
        """Test filtering readings for today."""
        client.force_login(user)
        
        # Create readings for today and yesterday
        today = timezone.now()
        yesterday = today - timezone.timedelta(days=1)
        
        today_reading = GlucoseReading.objects.create(
            occurred_at=today,
            value=Decimal("5.5"),
            unit="mmol/L",
            last_modified_by=user
        )
        yesterday_reading = GlucoseReading.objects.create(
            occurred_at=yesterday,
            value=Decimal("6.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        
        response = client.get(
            reverse("entries:glucose_readings_list"),
            {"filter": "today"}
        )
        
        assert response.status_code == 200
        readings = list(response.context["page_obj"])
        assert len(readings) == 1
        assert readings[0].id == today_reading.id
        assert response.context["filter_type"] == "today"

    def test_filter_yesterday(self, client, user):
        """Test filtering readings for yesterday."""
        client.force_login(user)
        
        # Create readings for today and yesterday
        today = timezone.now()
        yesterday = today - timezone.timedelta(days=1)
        
        today_reading = GlucoseReading.objects.create(
            occurred_at=today,
            value=Decimal("5.5"),
            unit="mmol/L",
            last_modified_by=user
        )
        yesterday_reading = GlucoseReading.objects.create(
            occurred_at=yesterday,
            value=Decimal("6.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        
        response = client.get(
            reverse("entries:glucose_readings_list"),
            {"filter": "yesterday"}
        )
        
        assert response.status_code == 200
        readings = list(response.context["page_obj"])
        assert len(readings) == 1
        assert readings[0].id == yesterday_reading.id
        assert response.context["filter_type"] == "yesterday"

    def test_filter_custom_date_range(self, client, user):
        """Test filtering readings with custom date range."""
        client.force_login(user)
        
        # Create readings across multiple days
        now = timezone.now()
        reading_day1 = GlucoseReading.objects.create(
            occurred_at=now - timezone.timedelta(days=5),
            value=Decimal("5.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        reading_day2 = GlucoseReading.objects.create(
            occurred_at=now - timezone.timedelta(days=3),
            value=Decimal("5.5"),
            unit="mmol/L",
            last_modified_by=user
        )
        reading_day3 = GlucoseReading.objects.create(
            occurred_at=now - timezone.timedelta(days=1),
            value=Decimal("6.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        
        # Filter for middle day only
        start_date = (now - timezone.timedelta(days=4)).strftime("%Y-%m-%d")
        end_date = (now - timezone.timedelta(days=2)).strftime("%Y-%m-%d")
        
        response = client.get(
            reverse("entries:glucose_readings_list"),
            {"start_date": start_date, "end_date": end_date}
        )
        
        assert response.status_code == 200
        readings = list(response.context["page_obj"])
        assert len(readings) == 1
        assert readings[0].id == reading_day2.id
        assert response.context["start_date"] == start_date
        assert response.context["end_date"] == end_date

    def test_filter_start_date_only(self, client, user):
        """Test filtering with only start date."""
        client.force_login(user)
        
        now = timezone.now()
        old_reading = GlucoseReading.objects.create(
            occurred_at=now - timezone.timedelta(days=5),
            value=Decimal("5.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        recent_reading1 = GlucoseReading.objects.create(
            occurred_at=now - timezone.timedelta(days=2),
            value=Decimal("5.5"),
            unit="mmol/L",
            last_modified_by=user
        )
        recent_reading2 = GlucoseReading.objects.create(
            occurred_at=now,
            value=Decimal("6.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        
        start_date = (now - timezone.timedelta(days=3)).strftime("%Y-%m-%d")
        
        response = client.get(
            reverse("entries:glucose_readings_list"),
            {"start_date": start_date}
        )
        
        assert response.status_code == 200
        readings = list(response.context["page_obj"])
        assert len(readings) == 2
        reading_ids = [r.id for r in readings]
        assert recent_reading1.id in reading_ids
        assert recent_reading2.id in reading_ids
        assert old_reading.id not in reading_ids

    def test_filter_end_date_only(self, client, user):
        """Test filtering with only end date."""
        client.force_login(user)
        
        now = timezone.now()
        old_reading1 = GlucoseReading.objects.create(
            occurred_at=now - timezone.timedelta(days=5),
            value=Decimal("5.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        old_reading2 = GlucoseReading.objects.create(
            occurred_at=now - timezone.timedelta(days=3),
            value=Decimal("5.5"),
            unit="mmol/L",
            last_modified_by=user
        )
        recent_reading = GlucoseReading.objects.create(
            occurred_at=now,
            value=Decimal("6.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        
        end_date = (now - timezone.timedelta(days=2)).strftime("%Y-%m-%d")
        
        response = client.get(
            reverse("entries:glucose_readings_list"),
            {"end_date": end_date}
        )
        
        assert response.status_code == 200
        readings = list(response.context["page_obj"])
        assert len(readings) == 2
        reading_ids = [r.id for r in readings]
        assert old_reading1.id in reading_ids
        assert old_reading2.id in reading_ids
        assert recent_reading.id not in reading_ids

    def test_filter_preserves_pagination(self, client, user):
        """Test that filtering works correctly with pagination."""
        client.force_login(user)
        
        # Create 30 readings for today (using different minutes to stay within today)
        today = timezone.now()
        today_start = today.replace(hour=8, minute=0, second=0, microsecond=0)
        for i in range(30):
            GlucoseReading.objects.create(
                occurred_at=today_start + timezone.timedelta(minutes=i * 10),
                value=Decimal("5.5"),
                unit="mmol/L",
                last_modified_by=user
            )
        
        # Create 20 readings for yesterday
        yesterday = today - timezone.timedelta(days=1)
        yesterday_start = yesterday.replace(hour=8, minute=0, second=0, microsecond=0)
        for i in range(20):
            GlucoseReading.objects.create(
                occurred_at=yesterday_start + timezone.timedelta(minutes=i * 10),
                value=Decimal("6.0"),
                unit="mmol/L",
                last_modified_by=user
            )
        
        # Filter for today with page size of 10
        response = client.get(
            reverse("entries:glucose_readings_list"),
            {"filter": "today", "page_size": "10"}
        )
        
        assert response.status_code == 200
        assert len(response.context["page_obj"]) == 10
        assert response.context["page_obj"].paginator.count == 30
        assert response.context["page_size"] == 10

    def test_no_filter_returns_all_readings(self, client, user):
        """Test that no filter returns all readings."""
        client.force_login(user)
        
        now = timezone.now()
        for i in range(5):
            GlucoseReading.objects.create(
                occurred_at=now - timezone.timedelta(days=i),
                value=Decimal("5.5"),
                unit="mmol/L",
                last_modified_by=user
            )
        
        response = client.get(reverse("entries:glucose_readings_list"))
        
        assert response.status_code == 200
        assert len(response.context["page_obj"]) == 5
        assert response.context["filter_type"] == ""
        assert response.context["start_date"] == ""
        assert response.context["end_date"] == ""


@pytest.mark.django_db
class TestGlucoseReadingCreateView:
    """Tests for glucose_reading_create view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:glucose_reading_create"))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_get_form_display(self, client, user):
        """Test that authenticated users can access the form."""
        client.force_login(user)
        response = client.get(reverse("entries:glucose_reading_create"))
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["title"] == "Add Blood Glucose Reading"
        assert "entries/glucose_reading_form.html" in [t.name for t in response.templates]

    def test_create_reading_success(self, client, user):
        """Test successful reading creation."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "value": "5.5",
            "unit": "mmol/L",
            "notes": "Before breakfast",
        }
        
        response = client.post(reverse("entries:glucose_reading_create"), data)
        
        # Should redirect to readings list
        assert response.status_code == 302
        assert response.url == reverse("entries:glucose_readings_list")
        
        # Reading should be created
        assert GlucoseReading.objects.count() == 1
        reading = GlucoseReading.objects.first()
        assert reading.value == Decimal("5.5")
        assert reading.unit == "mmol/L"
        assert reading.notes == "Before breakfast"
        assert reading.last_modified_by == user

    def test_create_reading_invalid_value(self, client, user):
        """Test that invalid form submission shows errors."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "value": "invalid",
            "unit": "mmol/L",
        }
        
        response = client.post(reverse("entries:glucose_reading_create"), data)
        
        # Should not redirect, show form with errors
        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()
        assert GlucoseReading.objects.count() == 0

    def test_create_reading_without_notes(self, client, user):
        """Test that notes field is optional."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "value": "6.2",
            "unit": "mg/dL",
        }
        
        response = client.post(reverse("entries:glucose_reading_create"), data)
        
        assert response.status_code == 302
        assert GlucoseReading.objects.count() == 1
        reading = GlucoseReading.objects.first()
        assert reading.notes == ""

    def test_create_reading_missing_required_fields(self, client, user):
        """Test that required fields are enforced."""
        client.force_login(user)
        
        # Missing occurred_at
        data = {
            "value": "5.5",
            "unit": "mmol/L",
        }
        
        response = client.post(reverse("entries:glucose_reading_create"), data)
        assert response.status_code == 200
        assert not response.context["form"].is_valid()
        assert GlucoseReading.objects.count() == 0


@pytest.mark.django_db
class TestGlucoseReadingEditView:
    """Tests for glucose_reading_edit view."""

    def test_view_requires_authentication(self, client, user):
        """Test that the view requires authentication."""
        reading = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.5"),
            unit="mmol/L",
            last_modified_by=user,
        )
        
        response = client.get(reverse("entries:glucose_reading_edit", args=[reading.pk]))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_get_edit_form_display(self, client, user):
        """Test that authenticated users can access the edit form."""
        reading = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.5"),
            unit="mmol/L",
            last_modified_by=user,
        )
        
        client.force_login(user)
        response = client.get(reverse("entries:glucose_reading_edit", args=[reading.pk]))
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["title"] == "Edit Blood Glucose Reading"
        assert response.context["reading"] == reading
        assert "entries/glucose_reading_form.html" in [t.name for t in response.templates]

    def test_edit_reading_success(self, client, user):
        """Test successful reading update."""
        reading = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.5"),
            unit="mmol/L",
            notes="Original note",
            last_modified_by=user,
        )
        
        client.force_login(user)
        
        new_time = timezone.now() + timezone.timedelta(hours=1)
        data = {
            "occurred_at": new_time.strftime("%Y-%m-%dT%H:%M"),
            "value": "6.8",
            "unit": "mg/dL",
            "notes": "Updated note",
        }
        
        response = client.post(reverse("entries:glucose_reading_edit", args=[reading.pk]), data)
        
        # Should redirect to readings list
        assert response.status_code == 302
        assert response.url == reverse("entries:glucose_readings_list")
        
        # Reading should be updated
        reading.refresh_from_db()
        assert reading.value == Decimal("6.8")
        assert reading.unit == "mg/dL"
        assert reading.notes == "Updated note"
        assert reading.last_modified_by == user

    def test_cannot_edit_other_users_reading(self, client, user, second_user):
        """Test that users cannot edit readings created by other users."""
        reading = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.5"),
            unit="mmol/L",
            last_modified_by=second_user,
        )
        
        client.force_login(user)
        response = client.get(reverse("entries:glucose_reading_edit", args=[reading.pk]))
        
        # Should redirect to readings list with error
        assert response.status_code == 302
        assert response.url == reverse("entries:glucose_readings_list")

    def test_edit_nonexistent_reading(self, client, user):
        """Test editing a reading that doesn't exist."""
        import uuid
        fake_uuid = uuid.uuid4()
        
        client.force_login(user)
        response = client.get(reverse("entries:glucose_reading_edit", args=[fake_uuid]))
        
        # Should redirect to readings list with error
        assert response.status_code == 302
        assert response.url == reverse("entries:glucose_readings_list")

    def test_edit_reading_invalid_value(self, client, user):
        """Test that invalid form submission shows errors."""
        reading = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.5"),
            unit="mmol/L",
            last_modified_by=user,
        )
        
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "value": "not_a_number",
            "unit": "mmol/L",
        }
        
        response = client.post(reverse("entries:glucose_reading_edit", args=[reading.pk]), data)
        
        # Should not redirect, show form with errors
        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()
        
        # Original value should be unchanged
        reading.refresh_from_db()
        assert reading.value == Decimal("5.5")

    def test_edit_preserves_timestamps(self, client, user):
        """Test that editing preserves created_at timestamp."""
        original_time = timezone.now() - timezone.timedelta(days=1)
        reading = GlucoseReading.objects.create(
            occurred_at=original_time,
            value=Decimal("5.5"),
            unit="mmol/L",
            last_modified_by=user,
        )
        original_created_at = reading.created_at
        
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "value": "6.0",
            "unit": "mmol/L",
        }
        
        response = client.post(reverse("entries:glucose_reading_edit", args=[reading.pk]), data)
        
        assert response.status_code == 302
        
        reading.refresh_from_db()
        # created_at should not change
        assert reading.created_at == original_created_at
        # but updated_at should be updated
        assert reading.updated_at > original_created_at


@pytest.mark.django_db
class TestMealsListView:
    """Tests for meals_list view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:meals_list"))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_view_with_authenticated_user(self, client, user):
        """Test that authenticated users can access the view."""
        client.force_login(user)
        response = client.get(reverse("entries:meals_list"))
        assert response.status_code == 200
        assert "entries/meals_list.html" in [t.name for t in response.templates]

    def test_pagination_default_page_size(self, client, user):
        """Test that default page size is 50."""
        client.force_login(user)
        
        # Create 75 meals
        for i in range(75):
            Meal.objects.create(
                occurred_at=timezone.now() - timezone.timedelta(hours=i),
                meal_type="breakfast",
                description=f"Test meal {i}",
                last_modified_by=user
            )
        
        response = client.get(reverse("entries:meals_list"))
        assert response.status_code == 200
        assert len(response.context["page_obj"]) == 50
        assert response.context["page_size"] == 50

    def test_pagination_custom_page_size(self, client, user):
        """Test custom page sizes."""
        client.force_login(user)
        
        # Create 30 meals
        for i in range(30):
            Meal.objects.create(
                occurred_at=timezone.now() - timezone.timedelta(hours=i),
                meal_type="lunch",
                description=f"Test meal {i}",
                last_modified_by=user
            )
        
        for page_size in [10, 25, 50, 100]:
            response = client.get(
                reverse("entries:meals_list"),
                {"page_size": page_size}
            )
            assert response.status_code == 200
            expected_items = min(page_size, 30)
            assert len(response.context["page_obj"]) == expected_items
            assert response.context["page_size"] == page_size

    def test_invalid_page_size_defaults_to_50(self, client, user):
        """Test that invalid page size defaults to 50."""
        client.force_login(user)
        
        # Test with invalid page size
        response = client.get(
            reverse("entries:meals_list"),
            {"page_size": "invalid"}
        )
        assert response.status_code == 200
        assert response.context["page_size"] == 50

    def test_meals_ordered_by_most_recent(self, client, user):
        """Test that meals are ordered by most recent first."""
        client.force_login(user)
        
        # Create meals with specific times
        older_meal = Meal.objects.create(
            occurred_at=timezone.now() - timezone.timedelta(hours=2),
            meal_type="breakfast",
            description="Older meal",
            last_modified_by=user
        )
        newer_meal = Meal.objects.create(
            occurred_at=timezone.now() - timezone.timedelta(hours=1),
            meal_type="dinner",
            description="Newer meal",
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:meals_list"))
        meals = list(response.context["page_obj"])
        
        # Newer meal should be first
        assert meals[0].id == newer_meal.id
        assert meals[1].id == older_meal.id

    def test_empty_meals_list(self, client, user):
        """Test view with no meals."""
        client.force_login(user)
        response = client.get(reverse("entries:meals_list"))
        assert response.status_code == 200
        assert len(response.context["page_obj"]) == 0

    def test_meals_display_with_carbs(self, client, user):
        """Test meals display with carbs information."""
        client.force_login(user)
        
        meal_with_carbs = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="lunch",
            description="Pasta with sauce",
            total_carbs=Decimal("45.5"),
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:meals_list"))
        assert response.status_code == 200
        meals = list(response.context["page_obj"])
        assert len(meals) == 1
        assert meals[0].total_carbs == Decimal("45.5")

    def test_meals_display_without_carbs(self, client, user):
        """Test meals display without carbs information."""
        client.force_login(user)
        
        meal_without_carbs = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="snack",
            description="Sugar-free snack",
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:meals_list"))
        assert response.status_code == 200
        meals = list(response.context["page_obj"])
        assert len(meals) == 1
        assert meals[0].total_carbs is None


@pytest.mark.django_db
class TestMealCreateView:
    """Tests for meal_create view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:meal_create"))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_get_form_display(self, client, user):
        """Test that authenticated users can access the form."""
        client.force_login(user)
        response = client.get(reverse("entries:meal_create"))
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["title"] == "Add Meal"
        assert "entries/meal_form.html" in [t.name for t in response.templates]

    def test_create_meal_success(self, client, user):
        """Test successful meal creation."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "meal_type": "breakfast",
            "description": "Oatmeal with berries and honey",
            "total_carbs": "45.5",
            "notes": "Felt good after",
        }
        
        response = client.post(reverse("entries:meal_create"), data)
        
        # Should redirect to meals list
        assert response.status_code == 302
        assert response.url == reverse("entries:meals_list")
        
        # Meal should be created
        assert Meal.objects.count() == 1
        meal = Meal.objects.first()
        assert meal.meal_type == "breakfast"
        assert meal.description == "Oatmeal with berries and honey"
        assert meal.total_carbs == Decimal("45.5")
        assert meal.notes == "Felt good after"
        assert meal.last_modified_by == user

    def test_create_meal_without_carbs(self, client, user):
        """Test that carbs field is optional."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "meal_type": "snack",
            "description": "Sugar-free jello",
        }
        
        response = client.post(reverse("entries:meal_create"), data)
        
        assert response.status_code == 302
        assert Meal.objects.count() == 1
        meal = Meal.objects.first()
        assert meal.total_carbs is None
        assert meal.notes == ""

    def test_create_meal_without_notes(self, client, user):
        """Test that notes field is optional."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "meal_type": "lunch",
            "description": "Grilled chicken salad",
            "total_carbs": "12.0",
        }
        
        response = client.post(reverse("entries:meal_create"), data)
        
        assert response.status_code == 302
        assert Meal.objects.count() == 1
        meal = Meal.objects.first()
        assert meal.notes == ""

    def test_create_meal_missing_required_fields(self, client, user):
        """Test that required fields are enforced."""
        client.force_login(user)
        
        # Missing description
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "meal_type": "dinner",
        }
        
        response = client.post(reverse("entries:meal_create"), data)
        assert response.status_code == 200
        assert not response.context["form"].is_valid()
        assert Meal.objects.count() == 0

    def test_create_meal_invalid_meal_type(self, client, user):
        """Test that invalid meal type is rejected."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "meal_type": "invalid_type",
            "description": "Test meal",
        }
        
        response = client.post(reverse("entries:meal_create"), data)
        assert response.status_code == 200
        assert not response.context["form"].is_valid()
        assert Meal.objects.count() == 0

    def test_create_meal_invalid_carbs(self, client, user):
        """Test that invalid carbs value shows errors."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "meal_type": "breakfast",
            "description": "Test meal",
            "total_carbs": "not_a_number",
        }
        
        response = client.post(reverse("entries:meal_create"), data)
        
        # Should not redirect, show form with errors
        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()
        assert Meal.objects.count() == 0

    def test_create_meal_all_meal_types(self, client, user):
        """Test creating meals with all valid meal types."""
        client.force_login(user)
        
        meal_types = ["breakfast", "lunch", "dinner", "snack"]
        
        for meal_type in meal_types:
            data = {
                "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
                "meal_type": meal_type,
                "description": f"Test {meal_type}",
            }
            
            response = client.post(reverse("entries:meal_create"), data)
            assert response.status_code == 302
        
        assert Meal.objects.count() == len(meal_types)
        created_types = set(Meal.objects.values_list("meal_type", flat=True))
        assert created_types == set(meal_types)


@pytest.mark.django_db
class TestMealEditView:
    """Tests for meal_edit view."""

    def test_view_requires_authentication(self, client, user):
        """Test that the view requires authentication."""
        meal = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="breakfast",
            description="Test meal",
            last_modified_by=user,
        )
        
        response = client.get(reverse("entries:meal_edit", args=[meal.pk]))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_get_edit_form_display(self, client, user):
        """Test that authenticated users can access the edit form."""
        meal = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="lunch",
            description="Grilled chicken salad",
            total_carbs=Decimal("25.0"),
            last_modified_by=user,
        )
        
        client.force_login(user)
        response = client.get(reverse("entries:meal_edit", args=[meal.pk]))
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["title"] == "Edit Meal"
        assert response.context["meal"] == meal
        assert "entries/meal_form.html" in [t.name for t in response.templates]

    def test_edit_meal_success(self, client, user):
        """Test successful meal update."""
        meal = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="breakfast",
            description="Original breakfast",
            total_carbs=Decimal("30.0"),
            notes="Original note",
            last_modified_by=user,
        )
        
        client.force_login(user)
        
        new_time = timezone.now() + timezone.timedelta(hours=1)
        data = {
            "occurred_at": new_time.strftime("%Y-%m-%dT%H:%M"),
            "meal_type": "lunch",
            "description": "Updated meal description",
            "total_carbs": "45.5",
            "notes": "Updated note",
        }
        
        response = client.post(reverse("entries:meal_edit", args=[meal.pk]), data)
        
        # Should redirect to meals list
        assert response.status_code == 302
        assert response.url == reverse("entries:meals_list")
        
        # Meal should be updated
        meal.refresh_from_db()
        assert meal.meal_type == "lunch"
        assert meal.description == "Updated meal description"
        assert meal.total_carbs == Decimal("45.5")
        assert meal.notes == "Updated note"
        assert meal.last_modified_by == user

    def test_cannot_edit_other_users_meal(self, client, user, second_user):
        """Test that users cannot edit meals created by other users."""
        meal = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="dinner",
            description="Other user's meal",
            last_modified_by=second_user,
        )
        
        client.force_login(user)
        response = client.get(reverse("entries:meal_edit", args=[meal.pk]))
        
        # Should redirect to meals list with error
        assert response.status_code == 302
        assert response.url == reverse("entries:meals_list")

    def test_edit_nonexistent_meal(self, client, user):
        """Test editing a meal that doesn't exist."""
        import uuid
        fake_uuid = uuid.uuid4()
        
        client.force_login(user)
        response = client.get(reverse("entries:meal_edit", args=[fake_uuid]))
        
        # Should redirect to meals list with error
        assert response.status_code == 302
        assert response.url == reverse("entries:meals_list")

    def test_edit_meal_invalid_data(self, client, user):
        """Test that invalid form submission shows errors."""
        meal = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="snack",
            description="Original snack",
            last_modified_by=user,
        )
        
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "meal_type": "invalid_type",
            "description": "Updated snack",
        }
        
        response = client.post(reverse("entries:meal_edit", args=[meal.pk]), data)
        
        # Should not redirect, show form with errors
        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()
        
        # Original values should be unchanged
        meal.refresh_from_db()
        assert meal.meal_type == "snack"

    def test_edit_meal_remove_carbs(self, client, user):
        """Test that carbs can be removed when editing."""
        meal = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="breakfast",
            description="Test meal",
            total_carbs=Decimal("30.0"),
            last_modified_by=user,
        )
        
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "meal_type": "breakfast",
            "description": "Test meal",
            "total_carbs": "",  # Empty to remove
        }
        
        response = client.post(reverse("entries:meal_edit", args=[meal.pk]), data)
        
        assert response.status_code == 302
        meal.refresh_from_db()
        assert meal.total_carbs is None

    def test_edit_preserves_timestamps(self, client, user):
        """Test that editing preserves created_at timestamp."""
        original_time = timezone.now() - timezone.timedelta(days=1)
        meal = Meal.objects.create(
            occurred_at=original_time,
            meal_type="breakfast",
            description="Test meal",
            last_modified_by=user,
        )
        original_created_at = meal.created_at
        
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "meal_type": "lunch",
            "description": "Updated meal",
        }
        
        response = client.post(reverse("entries:meal_edit", args=[meal.pk]), data)
        
        assert response.status_code == 302
        
        meal.refresh_from_db()
        # created_at should not change
        assert meal.created_at == original_created_at
        # but updated_at should be updated
        assert meal.updated_at > original_created_at

    def test_edit_meal_change_type(self, client, user):
        """Test changing meal type during edit."""
        meal = Meal.objects.create(
            occurred_at=timezone.now(),
            meal_type="breakfast",
            description="Morning meal",
            last_modified_by=user,
        )
        
        client.force_login(user)
        
        for new_type in ["lunch", "dinner", "snack"]:
            data = {
                "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
                "meal_type": new_type,
                "description": f"Changed to {new_type}",
            }
            
            response = client.post(reverse("entries:meal_edit", args=[meal.pk]), data)
            assert response.status_code == 302
            
            meal.refresh_from_db()
            assert meal.meal_type == new_type


@pytest.mark.django_db
class TestInsulinDosesListView:
    """Tests for insulin_doses_list view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:insulin_doses_list"))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_view_with_authenticated_user(self, client, user):
        """Test that authenticated users can access the view."""
        client.force_login(user)
        response = client.get(reverse("entries:insulin_doses_list"))
        assert response.status_code == 200
        assert "entries/insulin_doses_list.html" in [t.name for t in response.templates]

    def test_pagination_default_page_size(self, client, user, insulin_type):
        """Test that default page size is 50."""
        client.force_login(user)
        
        # Create 75 doses
        for i in range(75):
            InsulinDose.objects.create(
                occurred_at=timezone.now() - timezone.timedelta(hours=i),
                base_units=Decimal("10.0"),
                correction_units=Decimal("0.0"),
                insulin_type=insulin_type,
                last_modified_by=user
            )
        
        response = client.get(reverse("entries:insulin_doses_list"))
        assert response.status_code == 200
        assert len(response.context["page_obj"]) == 50
        assert response.context["page_size"] == 50

    def test_pagination_custom_page_size(self, client, user, insulin_type):
        """Test custom page sizes."""
        client.force_login(user)
        
        # Create 30 doses
        for i in range(30):
            InsulinDose.objects.create(
                occurred_at=timezone.now() - timezone.timedelta(hours=i),
                base_units=Decimal("5.0"),
                correction_units=Decimal("0.0"),
                insulin_type=insulin_type,
                last_modified_by=user
            )
        
        # Test page_size=10
        response = client.get(reverse("entries:insulin_doses_list"), {"page_size": 10})
        assert len(response.context["page_obj"]) == 10
        assert response.context["page_size"] == 10
        
        # Test page_size=25
        response = client.get(reverse("entries:insulin_doses_list"), {"page_size": 25})
        assert len(response.context["page_obj"]) == 25
        assert response.context["page_size"] == 25

    def test_doses_ordered_by_occurred_at_desc(self, client, user, insulin_type):
        """Test that doses are ordered by occurred_at descending."""
        client.force_login(user)
        
        # Create doses with different timestamps
        dose1 = InsulinDose.objects.create(
            occurred_at=timezone.now() - timezone.timedelta(hours=2),
            base_units=Decimal("8.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=user
        )
        dose2 = InsulinDose.objects.create(
            occurred_at=timezone.now() - timezone.timedelta(hours=1),
            base_units=Decimal("6.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=user
        )
        dose3 = InsulinDose.objects.create(
            occurred_at=timezone.now(),
            base_units=Decimal("10.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:insulin_doses_list"))
        doses = list(response.context["page_obj"])
        
        assert doses[0].pk == dose3.pk
        assert doses[1].pk == dose2.pk
        assert doses[2].pk == dose1.pk

    def test_empty_list_renders(self, client, user):
        """Test that the view renders correctly with no doses."""
        client.force_login(user)
        response = client.get(reverse("entries:insulin_doses_list"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestInsulinDoseCreateView:
    """Tests for insulin_dose_create view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:insulin_dose_create"))
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_get_view_renders_form(self, client, user):
        """Test that GET request renders the form."""
        client.force_login(user)
        response = client.get(reverse("entries:insulin_dose_create"))
        assert response.status_code == 200
        assert "entries/insulin_dose_form.html" in [t.name for t in response.templates]
        assert "form" in response.context
        assert response.context["title"] == "Add Insulin Dose"

    def test_create_dose_with_required_fields(self, client, user, insulin_type):
        """Test creating a dose with only required fields."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "base_units": "12.5",
            "correction_units": "0.0",
            "insulin_type": insulin_type.pk,
        }
        
        response = client.post(reverse("entries:insulin_dose_create"), data)
        assert response.status_code == 302
        assert response.url == reverse("entries:insulin_doses_list")
        
        # Verify dose was created
        dose = InsulinDose.objects.first()
        assert dose is not None
        assert dose.base_units == Decimal("12.5")
        assert dose.correction_units == Decimal("0.0")
        assert dose.insulin_type == insulin_type
        assert dose.last_modified_by == user
        assert dose.notes is None

    def test_create_dose_with_all_fields(self, client, user, insulin_type):
        """Test creating a dose with all fields."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "base_units": "15.0",
            "correction_units": "3.5",
            "insulin_type": insulin_type.pk,
            "notes": "Before dinner",
        }
        
        response = client.post(reverse("entries:insulin_dose_create"), data)
        assert response.status_code == 302
        
        dose = InsulinDose.objects.first()
        assert dose.base_units == Decimal("15.0")
        assert dose.correction_units == Decimal("3.5")
        assert dose.notes == "Before dinner"

    def test_create_dose_missing_required_field(self, client, user):
        """Test that missing required fields cause validation errors."""
        client.force_login(user)
        
        # Missing insulin_type
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "base_units": "10.0",
            "correction_units": "0.0",
        }
        
        response = client.post(reverse("entries:insulin_dose_create"), data)
        assert response.status_code == 200  # Form re-rendered with errors
        assert "form" in response.context
        assert response.context["form"].errors

    def test_create_dose_invalid_units(self, client, user, insulin_type):
        """Test validation for invalid units."""
        client.force_login(user)
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "base_units": "invalid",
            "correction_units": "0.0",
            "insulin_type": insulin_type.pk,
        }
        
        response = client.post(reverse("entries:insulin_dose_create"), data)
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_default_insulin_type_auto_selected(self, client, user):
        """Test that the default insulin type is automatically selected in the form."""
        from entries.models import InsulinType
        from base.middleware import set_current_user
        
        # Create a default insulin type
        set_current_user(user)
        default_type = InsulinType.objects.create(
            name="Default Type",
            type=InsulinType.Type.RAPID_ACTING,
            is_default=True
        )
        set_current_user(None)
        
        client.force_login(user)
        response = client.get(reverse("entries:insulin_dose_create"))
        
        assert response.status_code == 200
        assert "form" in response.context
        form = response.context["form"]
        
        # Check that the default insulin type is selected
        assert form.fields["insulin_type"].initial == default_type


@pytest.mark.django_db
class TestInsulinDoseEditView:
    """Tests for insulin_dose_edit view."""

    def test_view_requires_authentication(self, client, user, insulin_type):
        """Test that the view requires authentication."""
        dose = InsulinDose.objects.create(
            occurred_at=timezone.now(),
            base_units=Decimal("10.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=user
        )
        response = client.get(reverse("entries:insulin_dose_edit", args=[dose.pk]))
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_get_view_renders_form(self, client, user, insulin_type):
        """Test that GET request renders the form with existing data."""
        client.force_login(user)
        
        dose = InsulinDose.objects.create(
            occurred_at=timezone.now(),
            base_units=Decimal("8.5"),
            correction_units=Decimal("1.5"),
            insulin_type=insulin_type,
            notes="Test note",
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:insulin_dose_edit", args=[dose.pk]))
        assert response.status_code == 200
        assert "entries/insulin_dose_form.html" in [t.name for t in response.templates]
        assert "form" in response.context
        assert response.context["title"] == "Edit Insulin Dose"
        assert response.context["dose"] == dose

    def test_update_dose(self, client, user, insulin_type):
        """Test updating a dose."""
        client.force_login(user)
        
        dose = InsulinDose.objects.create(
            occurred_at=timezone.now(),
            base_units=Decimal("10.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=user
        )
        
        new_time = timezone.now() + timezone.timedelta(hours=1)
        data = {
            "occurred_at": new_time.strftime("%Y-%m-%dT%H:%M"),
            "base_units": "12.0",
            "correction_units": "2.0",
            "insulin_type": insulin_type.pk,
            "notes": "Updated notes",
        }
        
        response = client.post(reverse("entries:insulin_dose_edit", args=[dose.pk]), data)
        assert response.status_code == 302
        assert response.url == reverse("entries:insulin_doses_list")
        
        dose.refresh_from_db()
        assert dose.base_units == Decimal("12.0")
        assert dose.correction_units == Decimal("2.0")
        assert dose.notes == "Updated notes"
        assert dose.last_modified_by == user

    def test_user_can_only_edit_own_dose(self, client, user, another_user, insulin_type):
        """Test that users can only edit their own doses."""
        client.force_login(user)
        
        # Create dose by another user
        dose = InsulinDose.objects.create(
            occurred_at=timezone.now(),
            base_units=Decimal("10.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=another_user
        )
        
        response = client.get(reverse("entries:insulin_dose_edit", args=[dose.pk]))
        assert response.status_code == 404

    def test_nonexistent_dose_returns_404(self, client, user):
        """Test that editing a nonexistent dose returns 404."""
        client.force_login(user)
        
        from uuid import uuid4
        fake_uuid = uuid4()
        
        response = client.get(reverse("entries:insulin_dose_edit", args=[fake_uuid]))
        assert response.status_code == 404

    def test_update_dose_validation_errors(self, client, user, insulin_type):
        """Test that validation errors are handled properly."""
        client.force_login(user)
        
        dose = InsulinDose.objects.create(
            occurred_at=timezone.now(),
            base_units=Decimal("10.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=user
        )
        
        # Submit invalid data
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "base_units": "",  # Empty base_units
            "correction_units": "0.0",
            "insulin_type": insulin_type.pk,
        }
        
        response = client.post(reverse("entries:insulin_dose_edit", args=[dose.pk]), data)
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_switch_insulin_type(self, client, user, insulin_type):
        """Test changing insulin type on an existing dose."""
        client.force_login(user)
        
        # Create second insulin type
        new_type = InsulinType.objects.create(name="Long-acting")
        
        dose = InsulinDose.objects.create(
            occurred_at=timezone.now(),
            base_units=Decimal("10.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=user
        )
        
        data = {
            "occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "base_units": "10.0",
            "correction_units": "0.0",
            "insulin_type": new_type.pk,
        }
        
        response = client.post(reverse("entries:insulin_dose_edit", args=[dose.pk]), data)
        assert response.status_code == 302
        
        dose.refresh_from_db()
        assert dose.insulin_type == new_type


@pytest.mark.django_db
class TestActivityView:
    """Tests for activity view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:activity"))
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_view_with_authenticated_user(self, client, user):
        """Test that authenticated users can access the activity view."""
        client.force_login(user)
        response = client.get(reverse("entries:activity"))
        assert response.status_code == 200
        assert "entries/activity.html" in [t.name for t in response.templates]

    def test_activity_combines_all_entry_types(self, client, user, insulin_type):
        """Test that activity view combines glucose readings, insulin doses, and meals."""
        client.force_login(user)
        
        # Create entries with different times
        now = timezone.now()
        
        glucose = GlucoseReading.objects.create(
            occurred_at=now - timezone.timedelta(hours=3),
            value=5.5,
            unit="mmol/L",
            last_modified_by=user
        )
        
        dose = InsulinDose.objects.create(
            occurred_at=now - timezone.timedelta(hours=2),
            base_units=Decimal("10.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=user
        )
        
        meal = Meal.objects.create(
            occurred_at=now - timezone.timedelta(hours=1),
            meal_type="breakfast",
            description="Oatmeal",
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:activity"))
        assert response.status_code == 200
        
        # Check all entries are in the page
        entries = list(response.context["page_obj"])
        assert len(entries) == 3
        
        # Check they're sorted by newest first
        assert entries[0].pk == meal.pk
        assert entries[1].pk == dose.pk
        assert entries[2].pk == glucose.pk

    def test_activity_sorted_by_occurred_at_desc(self, client, user, insulin_type):
        """Test that activity is sorted by occurred_at in descending order."""
        client.force_login(user)
        
        now = timezone.now()
        
        # Create entries in mixed order
        old_glucose = GlucoseReading.objects.create(
            occurred_at=now - timezone.timedelta(days=5),
            value=5.5,
            unit="mmol/L",
            last_modified_by=user
        )
        
        recent_dose = InsulinDose.objects.create(
            occurred_at=now - timezone.timedelta(hours=1),
            base_units=Decimal("10.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=user
        )
        
        middle_meal = Meal.objects.create(
            occurred_at=now - timezone.timedelta(days=2),
            meal_type="lunch",
            description="Sandwich",
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:activity"))
        entries = list(response.context["page_obj"])
        
        # Verify order: newest first
        assert entries[0].pk == recent_dose.pk
        assert entries[1].pk == middle_meal.pk
        assert entries[2].pk == old_glucose.pk

    def test_today_filter(self, client, user, insulin_type):
        """Test filtering activity for today."""
        client.force_login(user)
        
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        
        # Create today's entry
        today_reading = GlucoseReading.objects.create(
            occurred_at=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()) + timezone.timedelta(hours=10)),
            value=5.5,
            unit="mmol/L",
            last_modified_by=user
        )
        
        # Create yesterday's entry
        yesterday_reading = GlucoseReading.objects.create(
            occurred_at=timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()) + timezone.timedelta(hours=10)),
            value=6.0,
            unit="mmol/L",
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:activity") + "?filter=today")
        assert response.status_code == 200
        
        entries = list(response.context["page_obj"])
        assert len(entries) == 1
        assert entries[0].pk == today_reading.pk

    def test_yesterday_filter(self, client, user, insulin_type):
        """Test filtering activity for yesterday."""
        client.force_login(user)
        
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        
        # Create today's entry
        today_reading = GlucoseReading.objects.create(
            occurred_at=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()) + timezone.timedelta(hours=10)),
            value=5.5,
            unit="mmol/L",
            last_modified_by=user
        )
        
        # Create yesterday's entry
        yesterday_reading = GlucoseReading.objects.create(
            occurred_at=timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()) + timezone.timedelta(hours=10)),
            value=6.0,
            unit="mmol/L",
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:activity") + "?filter=yesterday")
        assert response.status_code == 200
        
        entries = list(response.context["page_obj"])
        assert len(entries) == 1
        assert entries[0].pk == yesterday_reading.pk

    def test_custom_date_range_filter(self, client, user):
        """Test filtering activity with custom date range."""
        client.force_login(user)
        
        # Create entries across multiple days
        base_date = timezone.now().date() - timezone.timedelta(days=10)
        
        old_reading = GlucoseReading.objects.create(
            occurred_at=timezone.make_aware(timezone.datetime.combine(base_date, timezone.datetime.min.time())),
            value=5.0,
            unit="mmol/L",
            last_modified_by=user
        )
        
        middle_reading = GlucoseReading.objects.create(
            occurred_at=timezone.make_aware(timezone.datetime.combine(base_date + timezone.timedelta(days=5), timezone.datetime.min.time())),
            value=5.5,
            unit="mmol/L",
            last_modified_by=user
        )
        
        recent_reading = GlucoseReading.objects.create(
            occurred_at=timezone.make_aware(timezone.datetime.combine(base_date + timezone.timedelta(days=9), timezone.datetime.min.time())),
            value=6.0,
            unit="mmol/L",
            last_modified_by=user
        )
        
        # Filter for middle range
        start = (base_date + timezone.timedelta(days=3)).strftime("%Y-%m-%d")
        end = (base_date + timezone.timedelta(days=7)).strftime("%Y-%m-%d")
        
        response = client.get(f"{reverse('entries:activity')}?start_date={start}&end_date={end}")
        assert response.status_code == 200
        
        entries = list(response.context["page_obj"])
        assert len(entries) == 1
        assert entries[0].pk == middle_reading.pk

    def test_pagination(self, client, user):
        """Test pagination of activity entries."""
        client.force_login(user)
        
        # Create 15 glucose readings
        for i in range(15):
            GlucoseReading.objects.create(
                occurred_at=timezone.now() - timezone.timedelta(hours=i),
                value=5.0 + i * 0.1,
                unit="mmol/L",
                last_modified_by=user
            )
        
        # Request with page size of 10
        response = client.get(reverse("entries:activity") + "?page_size=10")
        assert response.status_code == 200
        
        page_obj = response.context["page_obj"]
        assert len(list(page_obj)) == 10
        assert page_obj.has_next()
        assert page_obj.paginator.num_pages == 2

    def test_empty_activity_list(self, client, user):
        """Test activity view with no entries."""
        client.force_login(user)
        
        response = client.get(reverse("entries:activity"))
        assert response.status_code == 200
        
        entries = list(response.context["page_obj"])
        assert len(entries) == 0

    def test_entry_type_attributes(self, client, user, insulin_type):
        """Test that entries have correct entry_type attributes."""
        client.force_login(user)
        
        now = timezone.now()
        
        glucose = GlucoseReading.objects.create(
            occurred_at=now - timezone.timedelta(hours=3),
            value=5.5,
            unit="mmol/L",
            last_modified_by=user
        )
        
        dose = InsulinDose.objects.create(
            occurred_at=now - timezone.timedelta(hours=2),
            base_units=Decimal("10.0"),
            correction_units=Decimal("0.0"),
            insulin_type=insulin_type,
            last_modified_by=user
        )
        
        meal = Meal.objects.create(
            occurred_at=now - timezone.timedelta(hours=1),
            meal_type="breakfast",
            description="Oatmeal",
            last_modified_by=user
        )
        
        response = client.get(reverse("entries:activity"))
        entries = list(response.context["page_obj"])
        
        # Find each entry and check its type
        meal_entry = next(e for e in entries if e.pk == meal.pk)
        dose_entry = next(e for e in entries if e.pk == dose.pk)
        glucose_entry = next(e for e in entries if e.pk == glucose.pk)
        
        assert meal_entry.entry_type == "meal"
        assert dose_entry.entry_type == "insulin"
        assert glucose_entry.entry_type == "glucose"


@pytest.mark.django_db
class TestInsulinSchedulesListView:
    """Tests for insulin_schedules_list view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:insulin_schedules_list"))
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_view_with_authenticated_user(self, client, user):
        """Test that authenticated users can access the schedules list."""
        client.force_login(user)
        response = client.get(reverse("entries:insulin_schedules_list"))
        assert response.status_code == 200
        assert "entries/insulin_schedules_list.html" in [t.name for t in response.templates]

    def test_schedules_ordered_by_time(self, client, user, insulin_type):
        """Test that schedules are ordered by time."""
        from entries.models import InsulinSchedule
        from datetime import time as dt_time
        
        client.force_login(user)
        
        # Create schedules in mixed order
        evening = InsulinSchedule.objects.create(
            label="Evening",
            time=dt_time(20, 0),
            insulin_type=insulin_type,
            units=15.0
        )
        
        morning = InsulinSchedule.objects.create(
            label="Morning",
            time=dt_time(8, 0),
            insulin_type=insulin_type,
            units=10.0
        )
        
        afternoon = InsulinSchedule.objects.create(
            label="Afternoon",
            time=dt_time(14, 0),
            insulin_type=insulin_type,
            units=12.0
        )
        
        response = client.get(reverse("entries:insulin_schedules_list"))
        schedules = list(response.context["schedules"])
        
        # Verify order: earliest time first
        assert schedules[0].pk == morning.pk
        assert schedules[1].pk == afternoon.pk
        assert schedules[2].pk == evening.pk

    def test_empty_schedules_list(self, client, user):
        """Test view with no schedules."""
        client.force_login(user)
        
        response = client.get(reverse("entries:insulin_schedules_list"))
        assert response.status_code == 200
        
        schedules = list(response.context["schedules"])
        assert len(schedules) == 0


@pytest.mark.django_db
class TestInsulinScheduleCreateView:
    """Tests for insulin_schedule_create view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:insulin_schedule_create"))
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_get_view_renders_form(self, client, user):
        """Test that GET request renders the form."""
        client.force_login(user)
        response = client.get(reverse("entries:insulin_schedule_create"))
        assert response.status_code == 200
        assert "entries/insulin_schedule_form.html" in [t.name for t in response.templates]
        assert "form" in response.context
        assert response.context["title"] == "Add Insulin Schedule"

    def test_create_schedule_with_required_fields(self, client, user, insulin_type):
        """Test creating a schedule with only required fields."""
        from entries.models import InsulinSchedule
        
        client.force_login(user)
        
        data = {
            "label": "Morning dose",
            "time": "08:00",
            "insulin_type": insulin_type.pk,
            "units": "10.5",
        }
        
        response = client.post(reverse("entries:insulin_schedule_create"), data)
        assert response.status_code == 302
        assert response.url == reverse("entries:insulin_schedules_list")
        
        # Verify schedule was created
        schedule = InsulinSchedule.objects.first()
        assert schedule is not None
        assert schedule.label == "Morning dose"
        assert schedule.units == Decimal("10.5")
        assert schedule.insulin_type == insulin_type
        assert schedule.notes is None

    def test_create_schedule_with_all_fields(self, client, user, insulin_type):
        """Test creating a schedule with all fields."""
        from entries.models import InsulinSchedule
        
        client.force_login(user)
        
        data = {
            "label": "Evening dose",
            "time": "20:00",
            "insulin_type": insulin_type.pk,
            "units": "15.0",
            "notes": "Before dinner",
        }
        
        response = client.post(reverse("entries:insulin_schedule_create"), data)
        assert response.status_code == 302
        
        schedule = InsulinSchedule.objects.first()
        assert schedule.label == "Evening dose"
        assert schedule.notes == "Before dinner"

    def test_create_schedule_missing_required_field(self, client, user):
        """Test that missing required fields cause validation errors."""
        client.force_login(user)
        
        # Missing time
        data = {
            "label": "Test",
            "insulin_type": "",
            "units": "10.0",
        }
        
        response = client.post(reverse("entries:insulin_schedule_create"), data)
        assert response.status_code == 200  # Form re-rendered with errors
        assert "form" in response.context
        assert response.context["form"].errors

    def test_create_schedule_invalid_units(self, client, user, insulin_type):
        """Test validation for invalid units."""
        client.force_login(user)
        
        data = {
            "label": "Test",
            "time": "08:00",
            "insulin_type": insulin_type.pk,
            "units": "invalid",
        }
        
        response = client.post(reverse("entries:insulin_schedule_create"), data)
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors


@pytest.mark.django_db
class TestInsulinScheduleEditView:
    """Tests for insulin_schedule_edit view."""

    def test_view_requires_authentication(self, client, insulin_type):
        """Test that the view requires authentication."""
        from entries.models import InsulinSchedule
        from datetime import time as dt_time
        
        schedule = InsulinSchedule.objects.create(
            label="Test",
            time=dt_time(8, 0),
            insulin_type=insulin_type,
            units=10.0
        )
        
        response = client.get(reverse("entries:insulin_schedule_edit", args=[schedule.pk]))
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_get_view_renders_form(self, client, user, insulin_type):
        """Test that GET request renders the form with existing data."""
        from entries.models import InsulinSchedule
        from datetime import time as dt_time
        
        client.force_login(user)
        
        schedule = InsulinSchedule.objects.create(
            label="Morning dose",
            time=dt_time(8, 0),
            insulin_type=insulin_type,
            units=10.0,
            notes="Before breakfast"
        )
        
        response = client.get(reverse("entries:insulin_schedule_edit", args=[schedule.pk]))
        assert response.status_code == 200
        assert "entries/insulin_schedule_form.html" in [t.name for t in response.templates]
        assert "form" in response.context
        assert response.context["title"] == "Edit Insulin Schedule"
        assert response.context["schedule"] == schedule

    def test_update_schedule(self, client, user, insulin_type):
        """Test updating a schedule."""
        from entries.models import InsulinSchedule
        from datetime import time as dt_time
        
        client.force_login(user)
        
        schedule = InsulinSchedule.objects.create(
            label="Morning dose",
            time=dt_time(8, 0),
            insulin_type=insulin_type,
            units=10.0
        )
        
        data = {
            "label": "Updated Morning dose",
            "time": "09:00",
            "insulin_type": insulin_type.pk,
            "units": "12.0",
            "notes": "Updated notes",
        }
        
        response = client.post(reverse("entries:insulin_schedule_edit", args=[schedule.pk]), data)
        assert response.status_code == 302
        assert response.url == reverse("entries:insulin_schedules_list")
        
        schedule.refresh_from_db()
        assert schedule.label == "Updated Morning dose"
        assert schedule.units == Decimal("12.0")
        assert schedule.notes == "Updated notes"

    def test_update_schedule_validation_errors(self, client, user, insulin_type):
        """Test that validation errors are displayed on update."""
        from entries.models import InsulinSchedule
        from datetime import time as dt_time
        
        client.force_login(user)
        
        schedule = InsulinSchedule.objects.create(
            label="Test",
            time=dt_time(8, 0),
            insulin_type=insulin_type,
            units=10.0
        )
        
        data = {
            "label": "",  # Empty label should fail
            "time": "08:00",
            "insulin_type": insulin_type.pk,
            "units": "10.0",
        }
        
        response = client.post(reverse("entries:insulin_schedule_edit", args=[schedule.pk]), data)
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_nonexistent_schedule_returns_404(self, client, user):
        """Test that editing a non-existent schedule returns 404."""
        import uuid
        
        client.force_login(user)
        
        fake_uuid = uuid.uuid4()
        response = client.get(reverse("entries:insulin_schedule_edit", args=[fake_uuid]))
        assert response.status_code == 404

    def test_switch_insulin_type(self, client, user, insulin_type):
        """Test changing insulin type on an existing schedule."""
        from entries.models import InsulinSchedule, InsulinType
        from datetime import time as dt_time
        from base.middleware import set_current_user
        
        client.force_login(user)
        
        # Create second insulin type
        set_current_user(user)
        new_type = InsulinType.objects.create(name="Long-acting", type="long")
        set_current_user(None)
        
        schedule = InsulinSchedule.objects.create(
            label="Test",
            time=dt_time(8, 0),
            insulin_type=insulin_type,
            units=10.0
        )
        
        data = {
            "label": "Test",
            "time": "08:00",
            "insulin_type": new_type.pk,
            "units": "10.0",
        }
        
        response = client.post(reverse("entries:insulin_schedule_edit", args=[schedule.pk]), data)
        assert response.status_code == 302
        
        schedule.refresh_from_db()
        assert schedule.insulin_type == new_type


@pytest.mark.django_db
class TestCorrectionScalesListView:
    """Tests for correction_scales_list view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:correction_scales_list"))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_view_with_authenticated_user(self, client, user):
        """Test that authenticated users can access the view."""
        client.force_login(user)
        response = client.get(reverse("entries:correction_scales_list"))
        assert response.status_code == 200
        assert "entries/correction_scales_list.html" in [t.name for t in response.templates]

    def test_pagination_default_page_size(self, client, user):
        """Test that default page size is 50."""
        client.force_login(user)
        
        # Create 75 correction scale entries
        for i in range(75):
            CorrectionScale.objects.create(
                greater_than=Decimal(f"{5 + i * 0.1:.1f}"),
                units_to_add=Decimal("1.0")
            )
        
        response = client.get(reverse("entries:correction_scales_list"))
        assert response.status_code == 200
        assert len(response.context["page_obj"]) == 50
        assert response.context["page_size"] == 50

    def test_pagination_custom_page_size(self, client, user):
        """Test custom page sizes."""
        client.force_login(user)
        
        # Create 30 entries
        for i in range(30):
            CorrectionScale.objects.create(
                greater_than=Decimal(f"{5 + i * 0.1:.1f}"),
                units_to_add=Decimal("1.0")
            )
        
        for page_size in [10, 25, 50, 100]:
            response = client.get(
                reverse("entries:correction_scales_list"),
                {"page_size": page_size}
            )
            assert response.status_code == 200
            expected_items = min(page_size, 30)
            assert len(response.context["page_obj"]) == expected_items
            assert response.context["page_size"] == page_size

    def test_scales_ordered_by_threshold(self, client, user):
        """Test that scales are ordered by greater_than threshold."""
        client.force_login(user)
        
        # Create scales in random order
        scale3 = CorrectionScale.objects.create(
            greater_than=Decimal("12.0"),
            units_to_add=Decimal("3.0")
        )
        scale1 = CorrectionScale.objects.create(
            greater_than=Decimal("8.0"),
            units_to_add=Decimal("1.0")
        )
        scale2 = CorrectionScale.objects.create(
            greater_than=Decimal("10.0"),
            units_to_add=Decimal("2.0")
        )
        
        response = client.get(reverse("entries:correction_scales_list"))
        scales = list(response.context["page_obj"])
        
        # Should be ordered by greater_than (ascending)
        assert scales[0] == scale1  # 8.0
        assert scales[1] == scale2  # 10.0
        assert scales[2] == scale3  # 12.0

    def test_empty_list_displays_message(self, client, user):
        """Test that empty list displays appropriate message."""
        client.force_login(user)
        
        response = client.get(reverse("entries:correction_scales_list"))
        assert response.status_code == 200
        # Check for empty state in the response
        assert "No correction scale entries found" in response.content.decode()


@pytest.mark.django_db
class TestCorrectionScaleCreateView:
    """Tests for correction_scale_create view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        response = client.get(reverse("entries:correction_scale_create"))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_view_with_authenticated_user(self, client, user):
        """Test that authenticated users can access the view."""
        client.force_login(user)
        response = client.get(reverse("entries:correction_scale_create"))
        assert response.status_code == 200
        assert "entries/correction_scale_form.html" in [t.name for t in response.templates]

    def test_create_correction_scale_with_valid_data(self, client, user):
        """Test creating a correction scale entry with valid data."""
        client.force_login(user)
        
        data = {
            "greater_than": "8.5",
            "units_to_add": "2.0",
        }
        
        response = client.post(reverse("entries:correction_scale_create"), data)
        
        # Should redirect to list view
        assert response.status_code == 302
        assert response.url == reverse("entries:correction_scales_list")
        
        # Verify the entry was created
        assert CorrectionScale.objects.count() == 1
        scale = CorrectionScale.objects.first()
        assert scale.greater_than == Decimal("8.5")
        assert scale.units_to_add == Decimal("2.0")

    def test_create_correction_scale_with_invalid_data(self, client, user):
        """Test creating a correction scale with invalid data."""
        client.force_login(user)
        
        data = {
            "greater_than": "invalid",
            "units_to_add": "2.0",
        }
        
        response = client.post(reverse("entries:correction_scale_create"), data)
        
        # Should not redirect (form has errors)
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors
        
        # Verify no entry was created
        assert CorrectionScale.objects.count() == 0

    def test_create_correction_scale_with_missing_fields(self, client, user):
        """Test creating a correction scale with missing required fields."""
        client.force_login(user)
        
        data = {
            "greater_than": "8.5",
            # Missing units_to_add
        }
        
        response = client.post(reverse("entries:correction_scale_create"), data)
        
        # Should not redirect (form has errors)
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors
        
        # Verify no entry was created
        assert CorrectionScale.objects.count() == 0


@pytest.mark.django_db
class TestCorrectionScaleEditView:
    """Tests for correction_scale_edit view."""

    def test_view_requires_authentication(self, client):
        """Test that the view requires authentication."""
        scale = CorrectionScale.objects.create(
            greater_than=Decimal("8.0"),
            units_to_add=Decimal("2.0")
        )
        
        response = client.get(reverse("entries:correction_scale_edit", args=[scale.pk]))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_view_with_authenticated_user(self, client, user):
        """Test that authenticated users can access the view."""
        client.force_login(user)
        
        scale = CorrectionScale.objects.create(
            greater_than=Decimal("8.0"),
            units_to_add=Decimal("2.0")
        )
        
        response = client.get(reverse("entries:correction_scale_edit", args=[scale.pk]))
        assert response.status_code == 200
        assert "entries/correction_scale_form.html" in [t.name for t in response.templates]

    def test_edit_correction_scale_with_valid_data(self, client, user):
        """Test editing a correction scale with valid data."""
        client.force_login(user)
        
        scale = CorrectionScale.objects.create(
            greater_than=Decimal("8.0"),
            units_to_add=Decimal("2.0")
        )
        
        data = {
            "greater_than": "9.5",
            "units_to_add": "3.0",
        }
        
        response = client.post(reverse("entries:correction_scale_edit", args=[scale.pk]), data)
        
        # Should redirect to list view
        assert response.status_code == 302
        assert response.url == reverse("entries:correction_scales_list")
        
        # Verify the entry was updated
        scale.refresh_from_db()
        assert scale.greater_than == Decimal("9.5")
        assert scale.units_to_add == Decimal("3.0")

    def test_edit_correction_scale_with_invalid_data(self, client, user):
        """Test editing a correction scale with invalid data."""
        client.force_login(user)
        
        scale = CorrectionScale.objects.create(
            greater_than=Decimal("8.0"),
            units_to_add=Decimal("2.0")
        )
        
        data = {
            "greater_than": "invalid",
            "units_to_add": "2.0",
        }
        
        response = client.post(reverse("entries:correction_scale_edit", args=[scale.pk]), data)
        
        # Should not redirect (form has errors)
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors
        
        # Verify the entry was not updated
        scale.refresh_from_db()
        assert scale.greater_than == Decimal("8.0")

    def test_edit_nonexistent_scale_returns_404(self, client, user):
        """Test editing a non-existent correction scale returns 404."""
        from uuid import uuid4
        client.force_login(user)
        
        # Try to access a non-existent scale
        fake_uuid = uuid4()
        response = client.get(reverse("entries:correction_scale_edit", args=[fake_uuid]))
        
        assert response.status_code == 404

    def test_form_prepopulated_with_scale_data(self, client, user):
        """Test that form is prepopulated with existing scale data."""
        client.force_login(user)
        
        scale = CorrectionScale.objects.create(
            greater_than=Decimal("10.5"),
            units_to_add=Decimal("2.5")
        )
        
        response = client.get(reverse("entries:correction_scale_edit", args=[scale.pk]))
        
        assert response.status_code == 200
        form = response.context["form"]
        assert form.initial["greater_than"] == Decimal("10.5")
        assert form.initial["units_to_add"] == Decimal("2.5")
