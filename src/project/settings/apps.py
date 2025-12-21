"""
Application configuration.
"""

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # allauth dependencies
    'django.contrib.sites',
    # allauth core
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # add providers as needed, e.g. 'allauth.socialaccount.providers.google',
    # local apps
    'base',
    'users',
]

SITE_ID = 1
