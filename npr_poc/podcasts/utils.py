from functools import lru_cache
import json
import logging

from django.conf import settings

from google.api_core.exceptions import GoogleAPIError
from google.cloud import speech
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_text_to_speech_client():
    service_account_info = json.loads(settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_CREDENTIALS)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    return speech.SpeechClient(credentials=credentials)


def transcribe_audio(media_obj):
    client = get_text_to_speech_client()
    # We are assuming here that the audio file is encoded with FLAC
    # Later we will need to convert all incoming audio to a format acceptable to
    # Google's speech-to-text API.
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=media_obj.sample_rate,
        language_code='en-US'
    )

    with media_obj.media_file.open('rb') as f:
        content = f.read()
    audio = speech.types.RecognitionAudio(content=content)
    try:
        response = client.recognize(config, audio, retry=None, timeout=30)
    except GoogleAPIError:
        logger.exception('Failed to query Google Speech-to-Text API')
        return []

    results = [result.alternatives[0].transcript for result in response.results]
    return results
