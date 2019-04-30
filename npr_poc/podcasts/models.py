import mimetypes
import os

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

import mutagen
from taggit.models import TaggedItemBase
from wagtailmedia.models import AbstractMedia

from npr_poc.utils.models import BasePage

from .edit_handlers import MediaChooserPanel
from .utils import transcribe_audio


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

    api_fields = [
        APIField('subtitle'),
        APIField('description'),
        APIField('podcast_type'),
        APIField('language'),
        APIField('tags'),
        APIField('is_explicit'),
        APIField('date_created'),
        APIField('date_updated'),
        APIField('license'),
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

    api_fields = [
        APIField('image'),
    ]


class CustomMedia(AbstractMedia):
    duration = models.DecimalField(null=True, decimal_places=2, max_digits=10, editable=False)
    bitrate = models.PositiveIntegerField(null=True, validators=[MinValueValidator(0)], editable=False)
    sample_rate = models.PositiveIntegerField(null=True, validators=[MinValueValidator(0)], editable=False)
    channels = models.PositiveSmallIntegerField(null=True, validators=[MinValueValidator(1)], editable=False)
    mime_type = models.CharField(max_length=20, blank=True, editable=False)

    transcript = models.TextField(blank=True, editable=False)

    def __str__(self):
        return self.title

    def save(self):
        ftype = mutagen.File(self.file.open())
        if ftype is not None:
            self.bitrate = ftype.info.bitrate or None
            self.sample_rate = ftype.info.sample_rate or None
            self.channels = ftype.info.channels or None
            self.duration = ftype.info.length or None

        mime_type = mimetypes.guess_type(self.file.name)
        self.mime_type = mime_type[0] or None

        # TODO we probably don't want to transcribe each enclosure, on the basis
        # that they should all contain the same content.
        if not self.transcript:
            self.file.seek(0, os.SEEK_SET)
            self.transcript = '\n\n'.join(transcribe_audio(self.file.read(), self.sample_rate))

        return super().save()

    admin_form_fields = (
        'title',
        'file',
        'collection',
        'tags',
    )


class EpisodeEnclosure(Orderable, models.Model):
    episode = ParentalKey(
        'podcasts.Episode',
        on_delete=models.CASCADE,
        related_name='enclosures',
    )
    media = models.ForeignKey(
        'podcasts.CustomMedia',
        models.PROTECT,
        null=True,
        related_name='+'
    )

    api_fields = [
        APIField('media'),
    ]

    panels = [
        MediaChooserPanel('media')
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
    is_explicit = models.BooleanField(default=False)

    search_fields = BasePage.search_fields + [
        index.SearchField('subtitle'),
        index.SearchField('description'),
        index.RelatedFields('enclosures', [
            index.RelatedFields('media', [
                index.SearchField('transcript'),
            ]),
        ]),
    ]

    api_fields = [
        APIField('subtitle'),
        APIField('description'),
        APIField('episode_type'),
        APIField('season_number'),
        APIField('tags'),
        APIField('is_explicit'),
        APIField('date_created'),
        APIField('date_updated'),
        APIField('enclosures'),
        APIField('images'),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('description'),
        FieldPanel('episode_type'),
        FieldPanel('tags'),
        FieldPanel('season_number'),
        FieldPanel('is_explicit'),
        InlinePanel('images', label='Images'),
        InlinePanel('enclosures', label='Enclosures'),
    ]
