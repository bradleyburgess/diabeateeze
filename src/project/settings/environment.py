"""
Environment and path configuration.
"""

import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Initialize environ
env = environ.Env(
    # Set default values and casting
    DEBUG=(bool, False),
    DJANGO_ENVIRONMENT=(str, "development"),
)

# Read .env file if it exists
environ.Env.read_env(BASE_DIR / ".env")

# Application version
VERSION = "1.0.5"

# Environment type (development, testing, production)
ENVIRONMENT = env("DJANGO_ENVIRONMENT")
