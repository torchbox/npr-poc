import mimetypes

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

import mutagen
from taggit.models import TaggedItemBase
from wagtailmedia.edit_handlers import MediaChooserPanel
from wagtailmedia.models import AbstractMedia

from npr_poc.utils.models import BasePage
from wagtail_headless_preview.models import HeadlessPreviewMixin

from .feeds import ShowFeed


class ShowTag(TaggedItemBase):
    content_object = ParentalKey(
        "podcasts.Show", on_delete=models.CASCADE, related_name="tagged_items"
    )


class ShowImage(Orderable, models.Model):
    image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL, models.CASCADE, related_name="+"
    )
    show = ParentalKey("podcasts.Show", on_delete=models.CASCADE, related_name="images")

    panels = [ImageChooserPanel("image")]

    api_fields = [
        APIField("image"),
        APIField(
            "image_thumbnail",
            serializer=ImageRenditionField("fill-798x530", source="image"),
        ),
    ]


class Show(HeadlessPreviewMixin, RoutablePageMixin, BasePage):
    template = "patterns/pages/podcasts/show_page.html"
    subpage_types = ["podcasts.Episode"]
    SHOW_TYPE_EPISODIC = "episodic"
    SHOW_TYPE_SERLIALIZED = "serialized"
    SHOW_TYPES = (
        (SHOW_TYPE_EPISODIC, "Episodic"),
        (SHOW_TYPE_SERLIALIZED, "Serialized"),
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    license = models.CharField(
        max_length=255, blank=True
    )  # This should probably be a set of choices later

    subtitle = models.CharField(max_length=255)
    description = RichTextField()

    podcast_type = models.CharField(max_length=255, choices=SHOW_TYPES)
    language = models.CharField(max_length=6, choices=settings.LANGUAGES, default="en")
    tags = ClusterTaggableManager(through=ShowTag, blank=True)
    is_explicit = models.BooleanField(default=False)

    search_fields = BasePage.search_fields + [
        index.SearchField("subtitle"),
        index.SearchField("description"),
    ]

    api_fields = [
        APIField("subtitle"),
        APIField("description"),
        APIField("podcast_type"),
        APIField("language"),
        APIField("tags"),
        APIField("is_explicit"),
        APIField("date_created"),
        APIField("date_updated"),
        APIField("license"),
        APIField("images"),
        APIField("feed_url"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("description"),
        InlinePanel("images", label="Images"),
    ]

    metadata_panels = [
        FieldPanel("license"),
        FieldPanel("podcast_type"),
        FieldPanel("language"),
        FieldPanel("tags"),
        FieldPanel("is_explicit"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(metadata_panels, heading="Metadata"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(
                BasePage.settings_panels, heading="Settings", classname="settings"
            ),
        ]
    )

    @route(r"^feed/$")
    def feed(self, request):
        return ShowFeed()(request, show_id=self.pk)

    @property
    def feed_url(self):
        return self.full_url + self.reverse_subpage("feed")


class EpisodeTag(TaggedItemBase):
    content_object = ParentalKey(
        "podcasts.Episode", on_delete=models.CASCADE, related_name="tagged_items"
    )


class EpisodeImage(Orderable, models.Model):
    image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL, models.CASCADE, related_name="+"
    )
    episode = ParentalKey(
        "podcasts.Episode", on_delete=models.CASCADE, related_name="images"
    )

    panels = [ImageChooserPanel("image")]

    api_fields = [
        APIField("image"),
        APIField(
            "image_thumbnail",
            serializer=ImageRenditionField("fill-798x530", source="image"),
        ),
    ]


class CustomMedia(AbstractMedia):
    duration = models.DecimalField(
        null=True, decimal_places=2, max_digits=10, editable=False
    )
    bitrate = models.PositiveIntegerField(
        null=True, validators=[MinValueValidator(0)], editable=False
    )
    sample_rate = models.PositiveIntegerField(
        null=True, validators=[MinValueValidator(0)], editable=False
    )
    channels = models.PositiveSmallIntegerField(
        null=True, validators=[MinValueValidator(1)], editable=False
    )
    mime_type = models.CharField(max_length=20, blank=True, editable=False)

    transcript = models.TextField(blank=True)
    is_transcribed = models.BooleanField(default=False, db_index=True)

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
        return super().save()

    admin_form_fields = ("title", "file", "collection", "tags", "transcript")


class EpisodeEnclosure(Orderable, models.Model):
    episode = ParentalKey(
        "podcasts.Episode", on_delete=models.CASCADE, related_name="enclosures"
    )
    media = models.ForeignKey(
        "podcasts.CustomMedia", models.CASCADE, null=True, related_name="+"
    )

    api_fields = [APIField("media")]

    panels = [MediaChooserPanel("media")]


class Episode(HeadlessPreviewMixin, BasePage):
    template = "patterns/pages/podcasts/episode_page.html"
    # Currently assuming that an episode can only be associated with one show.
    # If M2M relationships are allowed then this structure will need to change.
    parent_page_types = ["podcasts.Show"]
    subpage_types = []
    # We probably want to move this to an editable taxonomy
    EPISODE_TYPE_FULL = "full"
    EPISODE_TYPE_TRAILER = "trailer"
    EPISODE_TYPE_BONUS = "bonus"
    EPISODE_TYPES = (
        (EPISODE_TYPE_FULL, "Full"),
        (EPISODE_TYPE_TRAILER, "Trailer"),
        (EPISODE_TYPE_BONUS, "Bonus"),
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    subtitle = models.CharField(max_length=255)
    description = RichTextField()

    episode_type = models.CharField(max_length=255, choices=EPISODE_TYPES)
    tags = ClusterTaggableManager(through=EpisodeTag, blank=True)
    season_number = models.CharField(
        max_length=255, blank=True
    )  # Are seasons always numeric?
    is_explicit = models.BooleanField(default=False)

    def show(self):
        return self.get_parent().title

    search_fields = BasePage.search_fields + [
        index.SearchField("subtitle"),
        index.SearchField("description"),
        index.RelatedFields(
            "enclosures",
            [index.RelatedFields("media", [index.SearchField("transcript")])],
        ),
    ]

    share_with_npr = models.BooleanField(
        default=False,
        help_text="Allow this content to be published on NPR.org",
        verbose_name="Share with NPR.org",
    )
    share_with_member_stations = models.BooleanField(
        default=False,
        help_text="Allow this content to be published by NPR member stations",
        verbose_name="Share with NPR member stations",
    )

    api_fields = [
        APIField("subtitle"),
        APIField("description"),
        APIField("episode_type"),
        APIField("season_number"),
        APIField("tags"),
        APIField("is_explicit"),
        APIField("date_created"),
        APIField("date_updated"),
        APIField("enclosures"),
        APIField("images"),
        APIField("share_with_npr"),
        APIField("share_with_member_stations"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("description"),
        FieldPanel("episode_type"),
        FieldPanel("tags"),
        FieldPanel("season_number"),
        FieldPanel("is_explicit"),
        InlinePanel("images", label="Images"),
        InlinePanel("enclosures", label="Enclosures"),
    ]

    syndication_panels = [
        FieldPanel("share_with_npr"),
        FieldPanel("share_with_member_stations"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(syndication_panels, heading="Syndication"),
            ObjectList(
                BasePage.settings_panels, heading="Settings", classname="settings"
            ),
        ]
    )
