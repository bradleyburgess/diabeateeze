"""
Custom context processors for adding variables to all templates.
"""

from django.conf import settings


def version(request):
    """Add VERSION setting to template context."""
    return {"VERSION": settings.VERSION}


def allow_registrations(request):
    """Expose ALLOW_REGISTRATIONS setting to template context."""
    return {"ALLOW_REGISTRATIONS": settings.ALLOW_REGISTRATIONS}
