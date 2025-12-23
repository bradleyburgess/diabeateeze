"""Fixtures for entries app tests."""
import pytest
from entries.models import InsulinType
from base.middleware import set_current_user


@pytest.fixture
def insulin_type(user):
    """Create a test insulin type."""
    set_current_user(user)
    insulin_type = InsulinType.objects.create(
        name="Rapid-acting",
        type=InsulinType.Type.RAPID_ACTING,
        notes="Test insulin type"
    )
    set_current_user(None)
    return insulin_type
