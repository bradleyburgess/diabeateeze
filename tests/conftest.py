"""
Pytest configuration and fixtures for the project.
"""
import pytest
from django.contrib.auth import get_user_model
from entries.models import InsulinType

User = get_user_model()


@pytest.fixture
def user_data():
    """Sample user data for testing."""
    return {
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
    }


@pytest.fixture
def user(db, user_data):
    """Create a test user."""
    return User.objects.create_user(  # type: ignore[call-arg]
        email=user_data['email'],
        password=user_data['password'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
    )


@pytest.fixture
def second_user(db):
    """Create a second test user."""
    return User.objects.create_user(  # type: ignore[call-arg]
        email='test2@example.com',
        password='testpass123',
        first_name='Second',
        last_name='User',
    )


@pytest.fixture
def superuser(db):
    """Create a test superuser."""
    return User.objects.create_superuser(  # type: ignore[call-arg]
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User',
    )


@pytest.fixture
def another_user(db):
    """Create another test user for permission testing."""
    return User.objects.create_user(  # type: ignore[call-arg]
        email='another@example.com',
        password='testpass123',
        first_name='Another',
        last_name='User',
    )


@pytest.fixture
def insulin_type(db):
    """Create a test insulin type."""
    return InsulinType.objects.create(name="Rapid-acting")
