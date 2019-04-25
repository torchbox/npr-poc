from django.conf import settings
from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import CollectionMember, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from taggit.models import TaggedItemBase

from npr_poc.utils.models import BasePage


class ShowTag(TaggedItemBase):
    content_object = ParentalKey(
        'podcasts.Show',
        on_delete=models.CASCADE,
        related_name='tagged_items'
    )


class ShowImage(Orderable, models.Model):
    image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        models.CASCADE,
        related_name='+',
    )
    show = ParentalKey(
        'podcasts.Show',
        on_delete=models.CASCADE,
        related_name='images',
    )

    panels = [
        ImageChooserPanel('image'),
    ]


class Show(BasePage):
    template = 'patterns/pages/podcasts/show_page.html'
    subpage_types = ['podcasts.Episode']
    SHOW_TYPE_EPISODIC = 'episodic'
    SHOW_TYPE_SERLIALIZED = 'serialized'
    SHOW_TYPES = (
        (SHOW_TYPE_EPISODIC, 'Episodic'),
        (SHOW_TYPE_SERLIALIZED, 'Serialized'),
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    license = models.CharField(max_length=255, blank=True)      # This should probably be a set of choices later

    subtitle = models.CharField(max_length=255)
    description = RichTextField()

    podcast_type = models.CharField(max_length=255, choices=SHOW_TYPES)
    language = models.CharField(max_length=6, choices=settings.LANGUAGES, default='en')
    tags = ClusterTaggableManager(through=ShowTag, blank=True)
    is_explicit = models.BooleanField(default=False)

    search_fields = BasePage.search_fields + [
        index.SearchField('subtitle'),
        index.SearchField('description'),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('description'),
        FieldPanel('license'),
        FieldPanel('podcast_type'),
        FieldPanel('language'),
        FieldPanel('tags'),
        FieldPanel('is_explicit'),
        InlinePanel('images', label='Images'),
    ]


class EpisodeTag(TaggedItemBase):
    content_object = ParentalKey(
        'podcasts.Episode',
        on_delete=models.CASCADE,
        related_name='tagged_items'
    )


class EpisodeImage(Orderable, models.Model):
    image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        models.CASCADE,
        related_name='+',
    )
    episode = ParentalKey(
        'podcasts.Episode',
        on_delete=models.CASCADE,
        related_name='images',
    )

    panels = [
        ImageChooserPanel('image'),
    ]


class EpisodeEnclosure(CollectionMember, Orderable, models.Model):
    CHANNEL_MONO = 'mono'
    CHANNEL_STEREO = 'stereo'
    CHANNEL_CHOICES = (
        (CHANNEL_MONO, 'Mono'),
        (CHANNEL_STEREO, 'Stereo'),
    )

    episode = ParentalKey(
        'podcasts.Episode',
        on_delete=models.CASCADE,
        related_name='enclosures',
    )
    title = models.CharField(max_length=255)
    media_file = models.FileField(upload_to='media')
    date_created = models.DateTimeField(auto_now_add=True)

    # TODO see https://mutagen.readthedocs.io/en/latest/ for getting metadata from audio files
    file_size = models.PositiveIntegerField(null=True, editable=False)
    bitrate = models.PositiveIntegerField(null=True)
    sample_rate = models.PositiveIntegerField(null=True)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, blank=True)
    mime_type = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.title

    search_fields = CollectionMember.search_fields + [
        index.SearchField('title', partial_match=True, boost=10),
    ]

    panels = [
        FieldPanel('title'),
        FieldPanel('media_file'),   # TODO use a media chooser for this?
    ]


class Episode(BasePage):
    template = 'patterns/pages/podcasts/episode_page.html'
    # Currently assuming that an episode can only be associated with one show.
    # If M2M relationships are allowed then this structure will need to change.
    parent_page_types = ['podcasts.Show']
    subpage_types = []
    # We probably want to move this to an editable taxonomy
    EPISODE_TYPE_FULL = 'full'
    EPISODE_TYPE_TRAILER = 'trailer'
    EPISODE_TYPE_BONUS = 'bonus'
    EPISODE_TYPES = (
        (EPISODE_TYPE_FULL, 'Full'),
        (EPISODE_TYPE_TRAILER, 'Trailer'),
        (EPISODE_TYPE_BONUS, 'Bonus'),
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    subtitle = models.CharField(max_length=255)
    description = RichTextField()

    episode_type = models.CharField(max_length=255, choices=EPISODE_TYPES)
    tags = ClusterTaggableManager(through=EpisodeTag, blank=True)
    season_number = models.CharField(max_length=255, blank=True)        # Are seasons always numeric?
    duration = models.DurationField()
    is_explicit = models.BooleanField(default=False)

    search_fields = BasePage.search_fields + [
        index.SearchField('subtitle'),
        index.SearchField('description'),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('description'),
        FieldPanel('episode_type'),
        FieldPanel('tags'),
        FieldPanel('season_number'),
        FieldPanel('duration'),
        FieldPanel('is_explicit'),
        InlinePanel('images', label='Images'),
        InlinePanel('enclosures', label='Enclosures'),
    ]
