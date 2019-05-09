import os
import re
import feedparser
from npr_poc.news.models import NewsPage
from wagtail.core.models import Page

IMPORT_ROOT = "."

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
            "published": item.published_parsed,
            "summary": item.summary,
            "author": author,
            "text": cleanhtml(item.content[0]["value"]),
            "link": link,
        }
        items.append(d)
    return items


def insert(item):
    # create a news story in wagtail
    # skip previously imported items
    if NewsPage.objects.filter(source_link=item["link"]):
        print(item["title"] + "already exists, skipping")
    else:
        # start with parent as home page
        parent_page = Page.objects.get(id=3)
        news_page = NewsPage()
        news_page.title = item["title"]
        news_page.source_link = item["link"]
        news_page.date = item["published"]
        news_page.summary = item["summary"]
        # TODO: category, tags, author, streamfield
        parent_page.add_child(instance=news_page)
        print(f"inserting item {title}")


if __name__ == "__main__":
    for file in os.listdir(IMPORT_ROOT):
        if file.endswith(".xml"):
            for item in extract(file):
                insert(item)
