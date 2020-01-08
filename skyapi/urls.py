from django.urls import path

from skyapi.views import (
    auth_request,
    auth_callback,
)

urlpatterns = [
    path('oauth2/authrequest', auth_request),
    path('oauth2/callback', auth_callback),
]
