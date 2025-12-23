"""Model mixins for common functionality."""

from .middleware import get_current_user


class AutoLastModifiedMixin:
    """Mixin to automatically set last_modified_by field on save."""

    def save(self, *args, **kwargs):
        """Set last_modified_by to current user if not explicitly provided."""
        if hasattr(self, "last_modified_by"):
            current_user = get_current_user()
            if current_user and not self.last_modified_by_id:
                self.last_modified_by = current_user
        super().save(*args, **kwargs)
