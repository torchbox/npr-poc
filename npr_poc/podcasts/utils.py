import io
import json
import logging
import subprocess
import tempfile
from functools import lru_cache

from django.conf import settings
from django.core.files import File

import ffmpeg
from google.api_core.exceptions import GoogleAPIError
from google.cloud import speech, storage
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_text_to_speech_client():
    service_account_info = json.loads(settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_CREDENTIALS)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    return speech.SpeechClient(credentials=credentials)


@lru_cache(maxsize=1)
def get_storage_client():
    service_account_info = json.loads(settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_CREDENTIALS)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    return storage.Client(credentials=credentials, project=settings.GOOGLE_CLOUD_PROJECT_ID)


def get_flac_alternative(input_path):
    converted_file = tempfile.NamedTemporaryFile(delete=False)
    cmd = ffmpeg.input(input_path).output(
        converted_file.name, ac=1, format='flac'
    ).compile(overwrite_output=True)
    subp = subprocess.Popen(cmd)
    subp.communicate(timeout=60)
    with open(converted_file.name, 'rb') as output:
        content = output.read()
    return content


def transcribe_audio(media_file: File):
    # Pass either an absolute URL or absolute file path to ffmpeg
    input_path = media_file.url if media_file.url.startswith('http') else media_file.path
    data = ffmpeg.probe(input_path)
    stream = data['streams'][0]
    sample_rate = int(stream['sample_rate'])
    # Content must be a bytestream of audio encoded in FLAC, with a single channel
    if stream['channels'] == 1 and stream['codec_name'] == 'flac':
        content = media_file.read()
    else:
        content = get_flac_alternative(input_path)

    # Push the content to Cloud Storage, so the API can read it from there
    storage = get_storage_client()
    bucket = storage.get_bucket(settings.GOOGLE_CLOUD_BUCKET_NAME)
    blob_name = media_file.name + '.flac'
    blob = bucket.blob(blob_name)
    blob.upload_from_file(io.BytesIO(content), rewind=True, size=len(content))
    blob_uri = 'gs://{}/{}'.format(settings.GOOGLE_CLOUD_BUCKET_NAME, blob_name)

    client = get_text_to_speech_client()
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=sample_rate,
        language_code='en-US'
    )

    audio = speech.types.RecognitionAudio(uri=blob_uri)
    try:
        operation = client.long_running_recognize(config, audio, retry=None)
        response = operation.result()
    except GoogleAPIError:
        logger.exception('Failed to query Google Speech-to-Text API')
        return []

    # Clear object from storage
    bucket.delete_blob(blob_name)

    results = [result.alternatives[0].transcript for result in response.results]
    return results


def absurl(url):
    if url.startswith('/'):
        return settings.BASE_URL + url
    return url
