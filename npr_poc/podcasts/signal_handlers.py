from django.conf import settings
from django.core.management import call_command
from django.db.models.signals import post_save
from django.dispatch import receiver

import django_rq

from .models import CustomMedia


if settings.USE_REDIS_QUEUE:
    @receiver(post_save, sender=CustomMedia)
    def queue_transcription(sender, instance, **kwargs):
        if not instance.is_transcribed:
            django_rq.enqueue(call_command, 'transcribe_new_media', instance.pk)
