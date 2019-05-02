from django.core.management.base import BaseCommand

from npr_poc.podcasts.models import CustomMedia
from npr_poc.podcasts.utils import transcribe_audio


class Command(BaseCommand):
    help = 'Transcribe newly uploaded media'

    def handle(self, *args, **options):
        # For now, we just run this on all media with empty transcript.
        media = CustomMedia.objects.filter(type='audio', is_transcribed=False)
        for media_obj in media:
            if not media_obj.transcript:
                transcript_parts = transcribe_audio(media_obj.file)
                if transcript_parts:
                    media_obj.transcript = '\n\n'.join(transcript_parts)
                    self.stdout.write(
                        self.style.SUCCESS('Generated transcript for {}'.format(media_obj))
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('Unable to generate transcript for {}'.format(media_obj))
                    )
            media_obj.is_transcribed = True
            media_obj.save()
