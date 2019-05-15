from django.core.management.base import BaseCommand

from npr_poc.podcasts.models import CustomMedia
from npr_poc.podcasts.utils import transcribe_audio


class Command(BaseCommand):
    help = 'Transcribe newly uploaded media'

    def add_arguments(self, parser):
        parser.add_argument('media_id', nargs='?', type=int)

    def handle(self, *args, **options):
        media = CustomMedia.objects.filter(type='audio', is_transcribed=False)
        if options['media_id']:
            media = media.filter(pk=options['media_id'])

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
