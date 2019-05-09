import json

from django.conf import settings
from django.urls import reverse

from dateutil.parser import parse
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build


def get_flow():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        json.loads(settings.GOOGLE_OAUTH_CLIENT_CONFIG),
        scopes=[
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/documents.readonly'
        ]
    )
    flow.redirect_uri = settings.BASE_URL + reverse('npr_utils_google_oauth_complete')
    return flow


def get_auth_url():
    flow = get_flow()
    authorization_url, state = flow.authorization_url(access_type='offline')
    return authorization_url


def save_access_tokens_to_session(request, redirect_uri):
    flow = get_flow()
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials
    request.session['google_oauth_credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def search_documents(credentials, q=''):
    service = build('drive', 'v3', credentials=google.oauth2.credentials.Credentials(**credentials))
    name_query = 'and name contains "{}"'.format(q) if q else ''
    query = 'mimeType="application/vnd.google-apps.document" {}'.format(name_query)
    results = service.files().list(
        pageSize=10,
        orderBy='modifiedTime desc',
        fields="nextPageToken, files(id, name, webViewLink, modifiedTime)",
        q=query,
    ).execute()

    files = results.get('files', [])
    # Convert modifiedTime to a datetime object
    for f in files:
        f['modifiedTime'] = parse(f['modifiedTime'])

    return files
