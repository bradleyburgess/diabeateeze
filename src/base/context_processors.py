"""
Custom context processors for adding variables to all templates.
"""

from django.conf import settings


def version(request):
    """Add VERSION setting to template context."""
    return {"VERSION": settings.VERSION}
