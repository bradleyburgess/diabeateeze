"""
Tests for the custom User model.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests for the User model."""

    def test_create_user(self, user_data):
        """Test creating a regular user."""
        user = User.objects.create_user(**user_data)  # type: ignore[call-arg]
        assert user.email == user_data['email']
        assert user.first_name == user_data['first_name']
        assert user.last_name == user_data['last_name']
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password(user_data['password'])

    def test_create_user_without_email(self):
        """Test creating a user without an email raises ValueError."""
        with pytest.raises(ValueError, match='The Email field must be set'):
            User.objects.create_user(email='', password='testpass123')  # type: ignore[call-arg]

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(  # type: ignore[call-arg]
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
        )
        assert user.email == 'admin@example.com'
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_user_str_representation(self, user):
        """Test user string representation."""
        assert str(user) == user.email

    def test_get_full_name(self, user):
        """Test get_full_name method."""
        assert user.get_full_name() == f'{user.first_name} {user.last_name}'

    def test_get_full_name_no_names(self, db):
        """Test get_full_name returns formatted name."""
        user = User.objects.create_user(  # type: ignore[call-arg]
            email='test@example.com',
            password='pass',
            first_name='Jane',
            last_name='Smith',
        )
        assert user.get_full_name() == 'Jane Smith'

    def test_get_short_name(self, user):
        """Test get_short_name method."""
        assert user.get_short_name() == user.first_name

    def test_name_stripping(self, db):
        """Test that names are stripped of whitespace."""
        user = User.objects.create_user(  # type: ignore[call-arg]
            email='test@example.com',
            password='testpass',
            first_name='  John  ',
            last_name='  Doe  ',
        )
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
