import os
import re
import sys
from time import strftime
import feedparser
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from npr_poc.news.models import NewsPage, NewsCategory, NewsPageNewsCategory, Author
from wagtail.core.models import Page

IMPORT_ROOT = settings.IMPORT_ROOT
NEWS_PARENT_ID = settings.NEWS_PARENT_ID

cleanr = re.compile("<.*?>")


def cleanhtml(raw_html):
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


def extract(rss_file):
    f = feedparser.parse(rss_file)
    items = []
    for item in f.entries:
        try:
            author = item.author
        except AttributeError:
            author = "auto"
            print("couldn't find author for item " + item.title)
        if "?" in item.link:
            link = item.link.split("?")[0]
        else:
            link = item.link
        d = {
            "title": item.title,
            "published": strftime("%Y-%m-%d", item.published_parsed),
            "summary": item.summary,
            "author": author,
            "text": cleanhtml(item.content[0]["value"]),
            "link": link,
        }
        items.append(d)
    return items


class Command(BaseCommand):
    help = "Insert everything"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_id", nargs="+", type=int)

    def handle(self, *args, **options):

        self.news_category = NewsCategory.objects.get(slug="world-news")
        self.home_page = Page.objects.get(id=NEWS_PARENT_ID)

        for file in os.listdir(IMPORT_ROOT):
            if file.endswith(".xml"):
                for item in extract(os.path.join(IMPORT_ROOT, file)):
                    self.insert(item)

    def get_or_create_author(self, author_name):
        try:
            author = Author.objects.get(name=author_name)
        except Author.DoesNotExist:
            author = Author(name=author_name)
            author.save()
        return author

    def insert(self, item):
        # create a news story in wagtail
        # skip previously imported items
        if NewsPage.objects.filter(source_link=item["link"]):
            print(item["title"] + "already exists, skipping")
        else:
            # start with parent as home page
            parent_page = self.home_page
            news_page = NewsPage()
            title = item["title"]
            news_page.author = self.get_or_create_author(item["author"])
            news_page.title = title
            news_page.source_link = item["link"]
            news_page.date = item["published"]
            news_page.summary = item["summary"]
            # TODO: tags, author, streamfield
            parent_page.add_child(instance=news_page)
            npc = NewsPageNewsCategory()
            npc.page = news_page
            npc.category = self.news_category
            npc.save()
