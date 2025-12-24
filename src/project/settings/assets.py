"""
Static files and media configuration.
"""

from .environment import BASE_DIR

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# WhiteNoise settings - use CompressedManifestStaticFilesStorage
# This is needed when DEBUG=False to serve static files including admin
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
