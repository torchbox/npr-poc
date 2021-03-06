from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    InlinePanel,
    TabbedInterface,
    ObjectList,
)
from wagtail.api import APIField
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from npr_poc.utils.models import BasePage
from npr_poc.utils.blocks import StoryBlock
from taggit.models import TaggedItemBase, Tag as TaggitTag
from wagtail_content_import.models import ContentImportMixin


class NewsPageTag(TaggedItemBase):
    content_object = ParentalKey("NewsPage", related_name="news_tags")


class Tag(TaggitTag):
    class Meta:
        proxy = True


@register_snippet
class NewsCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


@register_snippet
class Author(index.Indexed, models.Model):
    name = models.CharField(max_length=255)

    panels = [FieldPanel("name")]

    search_fields = [index.SearchField("name", partial_match=True)]

    def __str__(self):
        return self.name


class NewsPageNewsCategory(models.Model):
    page = ParentalKey(
        "news.NewsPage", on_delete=models.CASCADE, related_name="categories"
    )
    category = models.ForeignKey(
        "news.NewsCategory", on_delete=models.CASCADE, related_name="news_pages"
    )

    panels = [SnippetChooserPanel("category")]

    class Meta:
        unique_together = ("page", "category")


class NewsIndexPage(Page):
    subpage_types = ["news.NewsPage", "syndication.SyndicatedNewsPage", "news.Thanks"]
    parent_page_types = ["home.HomePage"]


class NewsPage(ContentImportMixin, BasePage):
    subpage_types = []
    parent_page_types = ["news.NewsIndexPage"]
    date = models.DateField("Publish date")
    author = models.ForeignKey(
        "news.Author",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    summary = models.TextField(blank=True)
    body = StreamField(StoryBlock())
    # keep track of imported content
    source_link = models.URLField(blank=True, db_index=True)
    tags = ClusterTaggableManager(through="news.NewsPageTag", blank=True)

    legacy_id = models.CharField(blank=True, max_length=10)

    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.SearchField("body"),
    ]

    api_fields = [APIField("date"), APIField("summary")]

    content_panels = BasePage.content_panels + [
        FieldPanel("date"),
        SnippetChooserPanel("author"),
        FieldPanel("summary"),
        StreamFieldPanel("body"),
    ]

    taxonomy_panels = [InlinePanel("categories", label="category"), FieldPanel("tags")]

    settings_panels = BasePage.settings_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(taxonomy_panels, heading="Taxonomy"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )


class Thanks(BasePage):
    subpage_types = []
    parent_page_types = ["news.NewsIndexPage"]
    thanks_heading = models.CharField(max_length=255)
    thanks_body = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("thanks_heading"),
        FieldPanel("thanks_body"),
    ]
