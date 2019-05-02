from django.apps import AppConfig


class PodcastsConfig(AppConfig):
    name = 'npr_poc.podcasts'

    def ready(self):
        from . import signal_handlers      # noqa
