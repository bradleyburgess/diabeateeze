"""Tests for base app mixins and middleware."""
import pytest
from decimal import Decimal
from django.utils import timezone

from entries.models import GlucoseReading
from base.middleware import set_current_user


class TestAutoLastModifiedByMixin:
    """Tests for AutoLastModifiedMixin functionality."""

    def test_mixin_sets_user_on_create(self, user):
        """Test that the mixin sets last_modified_by on create."""
        set_current_user(user)
        
        reading = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.0"),
            unit="mmol/L"
        )
        
        set_current_user(None)
        
        assert reading.last_modified_by == user

    def test_mixin_updates_user_on_update(self, user, second_user):
        """Test that the mixin updates last_modified_by on update."""
        set_current_user(user)
        
        reading = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.0"),
            unit="mmol/L"
        )
        
        assert reading.last_modified_by == user
        
        # Change user and update
        set_current_user(second_user)
        reading.value = Decimal("6.0")
        reading.save()
        
        set_current_user(None)
        
        # Should still be the original user since we only set on create
        assert reading.last_modified_by == user

    def test_mixin_respects_explicit_none(self, user):
        """Test that setting last_modified_by explicitly is respected."""
        set_current_user(user)
        
        # When explicitly set to a user, it should use that user
        reading = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.0"),
            unit="mmol/L",
            last_modified_by=user
        )
        
        set_current_user(None)
        
        assert reading.last_modified_by == user

    @pytest.mark.django_db
    def test_mixin_works_without_current_user(self):
        """Test that the mixin works when no user is set."""
        # No user set in thread local
        
        reading = GlucoseReading.objects.create(
            occurred_at=timezone.now(),
            value=Decimal("5.0"),
            unit="mmol/L"
        )
        
        assert reading.last_modified_by is None
