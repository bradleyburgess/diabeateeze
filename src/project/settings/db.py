"""
Database configuration.
"""

import environ

from .environment import BASE_DIR, ENVIRONMENT, env

if ENVIRONMENT == "production":
    # PostgreSQL for production - all settings required
    try:
        DATABASES = {
            "default": env.db(
                "DATABASE_URL"
            )  # Expects postgresql://user:password@host:port/dbname
        }
    except environ.ImproperlyConfigured:
        raise ValueError(
            "Production environment requires DATABASE_URL to be set. "
            "Format: postgresql://user:password@host:port/dbname"
        )
else:
    # SQLite for development and testing
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
