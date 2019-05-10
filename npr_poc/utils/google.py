import json

from django.conf import settings
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.text import slugify

from bs4 import BeautifulSoup
from dateutil.parser import parse
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import requests

from npr_poc.images.models import CustomImage


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
    # We trigger consent prompt every time. This is a hack to get around
    # some rather stupid behaviour from Google's API, that only returns a refresh_token
    # when consent is first provided. See https://github.com/googleapis/google-api-python-client/issues/213 .
    # Later we will need to persist this refresh_token in the DB rather than in the session.
    authorization_url, state = flow.authorization_url(access_type='offline', prompt='consent')
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


def close_paragraph(block, stream_data):
    if block:
        stream_data.append({
            'type': 'paragraph',
            'value': ''.join(block)
        })
    block.clear()


def import_image(img_tag):
    # Create the image
    image = CustomImage(
        title=img_tag.alt or 'Imported from Google Docs',
    )
    response = requests.get(img_tag['src'])
    img_content = response.content
    img_file_name = slugify(image.title)
    img_content_type = response.headers.get('Content-Type', '')
    if img_content_type.startswith('image/'):
        # TODO we probably want to be a lot more discriminating here
        file_extension = img_content_type.split('/')[1]

    image.file.save('{}.{}'.format(img_file_name, file_extension), ContentFile(response.content))
    image.save()
    return image


def parse_document(credentials, doc_id):
    # We may want to use the docs API in future, as it provides a much more structured format
    service = build('drive', 'v3', credentials=google.oauth2.credentials.Credentials(**credentials))
    html = service.files().export_media(fileId=doc_id, mimeType='text/html').execute()
    metadata = service.files().get(fileId=doc_id, fields='name').execute()
    soup = BeautifulSoup(html)

    stream_data = []

    # Run through contents and populate stream
    current_paragraph_block = []

    for tag in soup.body.contents:
        if tag.name == 'h1':
            close_paragraph(current_paragraph_block, stream_data)
            # Wagtail will render this as a h2
            stream_data.append({'type': 'heading', 'value': tag.text})
        elif tag.name == 'h2':
            close_paragraph(current_paragraph_block, stream_data)
            # h2 > h3
            current_paragraph_block = ['<h3>{}</h3>'.format(tag.text)]
        elif tag.name in ['h3', 'h4', 'h5', 'h6']:
            # Rich text field only allows h3 and h4 by default, so we just set to h4
            current_paragraph_block.append('<h4>{}</h4>'.format(tag.text))
        elif tag.name == 'img':
            # Break the paragraph and add an image
            close_paragraph(current_paragraph_block, stream_data)
            image = import_image(tag)
            stream_data.append({'type': 'image', 'value': {'image': image.pk}})
        elif tag.text:
            current_paragraph_block.append(str(tag))
        if tag.find_all('img'):
            # Break the paragraph and add images
            close_paragraph(current_paragraph_block, stream_data)
            for img in tag.find_all('img'):
                image = import_image(img)
                stream_data.append({'type': 'image', 'value': {'image': image.pk}})

    close_paragraph(current_paragraph_block, stream_data)

    return metadata['name'], stream_data
