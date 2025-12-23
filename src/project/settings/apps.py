"""
Application configuration.
"""

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # allauth dependencies
    "django.contrib.sites",
    # allauth core
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # add providers as needed, e.g. 'allauth.socialaccount.providers.google',
    # crispy forms
    "crispy_forms",
    "crispy_bootstrap5",
    # local apps
    "base",
    "users",
    "entries",
    "dashboard",
]

SITE_ID = 1

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
