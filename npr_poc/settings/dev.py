import os

from .base import *  # noqa

# Debugging to be enabled locally only
DEBUG = True


# This key to be used locally only.
SECRET_KEY = 'foo'

# Enable FE component library
PATTERN_LIBRARY_ENABLED = True

# Allow all the hosts locally only.
ALLOWED_HOSTS = ['*']


# Allow requests from the local IPs to see more debug information.
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2')


# This is only to test Wagtail emails.
BASE_URL = 'http://localhost:8000'


# Display sent emails in the console while developing locally.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Disable password validators when developing locally.
AUTH_PASSWORD_VALIDATORS = []


# Enable Wagtail's style guide in Wagtail's settings menu.
# http://docs.wagtail.io/en/stable/contributing/styleguide.html

# Adds django-extensions into installed apps
INSTALLED_APPS += ['django_extensions']  # noqa


# Disable forcing HTTPS locally since development server supports HTTP only.
SECURE_SSL_REDIRECT = False


# This allows oAuth to work locally over http
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# Adds Django Debug Toolbar, if preset
try:
    import debug_toolbar  # noqa
    INSTALLED_APPS.append('debug_toolbar')  # noqa
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa
except ImportError:
    pass

# Import settings from local.py file if it exists. Please use it to keep
# settings that are not meant to be checked into Git and never check it in.
try:
    from .local import *  # noqa
except ImportError:
    pass
