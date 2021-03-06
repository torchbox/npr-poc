# Most of the settings are set in base.py, that's why this file appears fairly
# empty.
from .base import *  # noqa

# Explicitly disable debug mode in production
DEBUG = False

# Security configuration

# When set to True, client-side JavaScript will not to be able to access the CSRF cookie.
# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True

# Ensure that the session cookie is only sent by browsers under an HTTPS connection.
# https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True

# Ensure that the CSRF cookie is only sent by browsers under an HTTPS connection.
# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True

WAGTAILCONTENTIMPORT_GOOGLE_PICKER_API_KEY = os.getenv('WAGTAILCONTENTIMPORT_GOOGLE_PICKER_API_KEY', '')
WAGTAILCONTENTIMPORT_GOOGLE_OAUTH_CLIENT_CONFIG = os.getenv('WAGTAILCONTENTIMPORT_GOOGLE_OAUTH_CLIENT_CONFIG', '')
WAGTAILCONTENTIMPORT_MICROSOFT_CLIENT_ID = os.getenv('WAGTAILCONTENTIMPORT_MICROSOFT_CLIENT_ID', '')
