import json
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.text import slugify

from bs4 import BeautifulSoup, NavigableString
from dateutil.parser import parse
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import requests
from requests.exceptions import MissingSchema

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


def create_streamfield_block(**kwargs):
    # Add an ID to the block, because wagtail-react-streamfield borks without one
    kwargs['id'] = str(uuid.uuid4())
    return kwargs


def close_paragraph(block, stream_data):
    if block:
        stream_data.append(create_streamfield_block(type='paragraph', value=''.join(block)))
    block.clear()


def import_image(img_tag):
    if not img_tag.get('src') or '/tracking/' in img_tag['src'] or '__utm.gif' in img_tag['src']:
        return

    try:
        response = requests.get(img_tag['src'])
    except MissingSchema:
        return

    if not response.status_code == 200:
        return

    img_content = response.content
    img_title = img_tag.get('alt', '')
    img_file_name = slugify(img_title) if img_title else uuid.uuid4()
    img_content_type = response.headers.get('Content-Type', '')
    if img_content_type.startswith('image/'):
        # TODO we probably want to be a lot more discriminating here
        file_extension = img_content_type.split('/')[1]
    else:
        # Don't mess with what isn't an image
        return

    img_file_name = '{}.{}'.format(img_file_name, file_extension)

    # Create the image
    image = CustomImage(
        title=img_title or img_file_name,
    )

    image.file.save(img_file_name, ContentFile(response.content))
    image.save()
    return image


def html_to_stream_data(html):
    soup = BeautifulSoup(html)

    stream_data = []

    # Run through contents and populate stream
    current_paragraph_block = []

    for tag in soup.body.recursiveChildGenerator():
        # Remove all inline styles and classes
        if hasattr(tag, 'attrs'):
            for attr in ['class', 'style']:
                tag.attrs.pop(attr, None)

    for tag in soup.body.contents:
        if isinstance(tag, NavigableString):
            stream_data.append(create_streamfield_block(type='paragraph', value=str(tag)))
        else:
            if tag.name == 'h1':
                close_paragraph(current_paragraph_block, stream_data)
                # Wagtail will render this as a h2
                stream_data.append(create_streamfield_block(type='heading', value=tag.text))
            elif tag.name == 'h2':
                close_paragraph(current_paragraph_block, stream_data)
                # h2 > h3
                current_paragraph_block = ['<h3>{}</h3>'.format(tag.text)]
            elif tag.name in ['h3', 'h4', 'h5', 'h6']:
                # Rich text field only allows h3 and h4 by default, so we just set to h4
                current_paragraph_block.append('<h4>{}</h4>'.format(tag.text))
            elif tag.name == 'img':
                image = import_image(tag)
                if image:
                    # Break the paragraph and add an image
                    close_paragraph(current_paragraph_block, stream_data)
                    stream_data.append(create_streamfield_block(type='image', value={'image': image.pk}))
            elif tag.text:
                current_paragraph_block.append(str(tag))

            if tag.find_all('img'):
                # Break the paragraph and add images
                close_paragraph(current_paragraph_block, stream_data)
                for img in tag.find_all('img'):
                    image = import_image(img)
                    if image:
                        stream_data.append(create_streamfield_block(type='image', value={'image': image.pk}))

    close_paragraph(current_paragraph_block, stream_data)

    return stream_data


def parse_document(credentials, doc_id):
    # We may want to use the docs API in future, as it provides a much more structured format
    service = build('drive', 'v3', credentials=google.oauth2.credentials.Credentials(**credentials))
    html = service.files().export_media(fileId=doc_id, mimeType='text/html').execute()
    metadata = service.files().get(fileId=doc_id, fields='name').execute()
    return metadata['name'], html_to_stream_data(html)
