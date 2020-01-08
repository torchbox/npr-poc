import requests

from django.shortcuts import redirect

APPLICATION_ID = '91f557bf-3489-4405-a3dd-25bc8ed2880b'
REDIRECT_URI = 'http://localhost:8000/skyapi/oauth2/callback'


def auth_request(request):
    url = f'https://oauth2.sky.blackbaud.com/authorization?client_id={APPLICATION_ID}&response_type=code&redirect_uri={REDIRECT_URI}&state=somevalue'
    redirect(url)


def auth_callback(request):
    auth_code = request.GET.get('code')

    