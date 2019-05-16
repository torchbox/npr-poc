import json

import feedparser
import os
import re

from time import strftime

from django.core.management.base import BaseCommand
from django.conf import settings
from wagtail.core.models import Page

from npr_poc.news.models import Author, NewsCategory, NewsPage, NewsPageNewsCategory
from npr_poc.utils.google import html_to_stream_data

IMPORT_ROOT_PATH = settings.IMPORT_ROOT_PATH

cleanr = re.compile("<.*?>")


def cleanhtml(raw_html):
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


def extract(rss_file):
    f = feedparser.parse(rss_file)
    items = []

    for item in f.entries:
        title = item.title.encode('ascii', 'xmlcharrefreplace').decode('utf-8')
        try:
            author = item.nprml_byline['name']
        except (AttributeError, KeyError):
            author = "auto"
            print("couldn't find author for item " + title)
        if "?" in item.link:
            link = item.link.split("?")[0]
        else:
            link = item.link

        d = {
            "title": title,
            "published": strftime("%Y-%m-%d", item.published_parsed),
            "summary": item.summary,
            "author": author,
            "html": item.nprml_textwithhtml,
            "link": link,
        }
        items.append(d)
    return items


class Command(BaseCommand):
    help = """
Using the XML from
http://api.npr.org/query?orgId=314&apiKey=<KEY_HERE>&fields=title,teaser,storyDate,byline,textWithHtml&output=RSS&numResults={PAGE_SIZE}
taken with a variation of news_import.py

Files prepped with regex search/replace:
Search: <nprml:byline id="(\d+)">(\n\s+)(<nprml:name .*>(.*)</nprml:name>)
Replace: <nprml:byline id="$1" name="$4">$2$3
"""

    def add_arguments(self, parser):
        parser.add_argument(
            'parent_page_id',
            type=int,
            help='The ID of the page to import the files under'
        )

    def handle(self, *args, **options):

        self.news_category = NewsCategory.objects.get(slug="world-news")
        self.parent = Page.objects.get(id=options['parent_page_id'])

        for file in os.listdir(IMPORT_ROOT_PATH):
            if file.endswith(".xml"):
                for item in extract(os.path.join(IMPORT_ROOT_PATH, file)):
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
            parent_page = self.parent
            news_page = NewsPage()
            title = item["title"]
            news_page.author = self.get_or_create_author(item["author"])
            news_page.title = title
            news_page.source_link = item["link"]
            news_page.date = item["published"]
            news_page.summary = item["summary"]
            news_page.body = json.dumps(html_to_stream_data(item["html"]))
            parent_page.add_child(instance=news_page)
            npc = NewsPageNewsCategory()
            npc.page = news_page
            npc.category = self.news_category
            npc.save()
