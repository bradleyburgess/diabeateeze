"""
Security-related settings.
"""

from .environment import env, ENVIRONMENT

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-s70y=-2!)zx$uknn%yaufojq9h^8kk4b39x+pz!uvy6p8=tz(2"
)

# Raise error if using default secret key in production
if ENVIRONMENT == "production" and "django-insecure" in SECRET_KEY:
    raise ValueError(
        "You must set a unique SECRET_KEY in production. "
        "Generate one with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True if ENVIRONMENT != "production" else False)

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"] if ENVIRONMENT != "production" else [])
