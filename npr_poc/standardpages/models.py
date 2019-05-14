from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.core.fields import StreamField, RichTextField
from wagtail.search import index

from npr_poc.utils.blocks import StoryBlock
from npr_poc.utils.models import BasePage, RelatedPage


class InformationPageRelatedPage(RelatedPage):
    source_page = ParentalKey("InformationPage", related_name="related_pages")


class InformationPage(BasePage):
    template = "patterns/pages/standardpages/information_page.html"

    introduction = models.TextField(blank=True)
    body = StreamField(StoryBlock())

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        StreamFieldPanel("body"),
        InlinePanel("related_pages", label="Related pages"),
    ]


class IndexPage(BasePage):
    template = "patterns/pages/standardpages/index_page.html"

    introduction = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [FieldPanel("introduction")]

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        subpages = self.get_children().live()
        per_page = settings.DEFAULT_PER_PAGE
        page_number = request.GET.get("page")
        paginator = Paginator(subpages, per_page)

        try:
            subpages = paginator.page(page_number)
        except PageNotAnInteger:
            subpages = paginator.page(1)
        except EmptyPage:
            subpages = paginator.page(paginator.num_pages)

        context["subpages"] = subpages

        return context


class RichTextPage(BasePage):
    parent_page_types = ["standardpages.IndexPage"]
    quite_rich_text = RichTextField(
        features=["h2", "h3", "bold"],
        blank=True,
        help_text="A rich text field with few very formatting options",
    )
    very_rich_text = RichTextField(
        features=[
            "h2",
            "h3",
            "h4",
            "h5",
            "bold",
            "italic",
            "hr",
            "document-link",
            "image",
            "code",
        ],
        blank=True,
        help_text="A rich text field with many formatting options",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("quite_rich_text"),
        FieldPanel("very_rich_text"),
    ]
