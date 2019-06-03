from django.db import models

from wagtail.admin.edit_handlers import FieldPanel

from npr_poc.utils.models import BasePage

from .utils import get_story
from .widgets import SyndicatedContentChooser


class SyndicatedNewsPage(BasePage):
    parent_page_types = ["news.NewsIndexPage"]
    subpage_types = []
    template = "patterns/pages/syndication/syndicated_news_page.html"
    story = models.CharField(max_length=255, db_index=True)
    date = models.DateField("Publish date")

    content_panels = [FieldPanel("story", widget=SyndicatedContentChooser)]

    def clean(self):
        story = get_story(self.story)
        self.title = story["title"]
        self.date = story["date"]

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx["story"] = get_story(self.story)
        return ctx

    class Meta:
        verbose_name_plural = "Syndicated News"


class PBSShowPage(BasePage):
    pass
