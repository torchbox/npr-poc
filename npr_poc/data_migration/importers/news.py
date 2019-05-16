import json
from datetime import datetime

import pytz
from django.utils import timezone

from npr_poc.news.models import NewsPage, Author
from npr_poc.standardpages.models import IndexPage
from npr_poc.utils.google import html_to_stream_data

from .base import BasePageImporter


class NewsImporter(BasePageImporter):
    """
    Example use of the BasePageImporter for importing a specific page type
    """

    parent_page_model = IndexPage
    content_model = NewsPage
    legacy_id_field = 'nid'
    source_str_field = 'title'
    imported_str_field = 'slug'
    field_mapping = (
        # local key, import key, truncation length
        ('title', source_str_field, 255),
        # ('summary', 'summary', None),
        ('body', 'body', None),
        ('legacy_id', legacy_id_field, None),
        ('date', 'first_published_at', None),
        ('first_published_at', 'first_published_at', None)
    )
    timezone = pytz.timezone('US/Eastern')
    description = "News Page"

    def format_data(self, data):
        """ Overridden to add a body field """
        formatted_data = super().format_data(data)

        body = html_to_stream_data(formatted_data['body'])
        formatted_data['body'] = json.dumps(body)

        date = self.get_date(formatted_data, 'date')
        formatted_data['date'] = date.strftime('%Y-%m-%d')

        return formatted_data

    def get_or_create_author(self, author_name):
        try:
            author = Author.objects.get(name=author_name)
        except Author.DoesNotExist:
            author = Author(name=author_name)
            author.save()
        return author

    def post_process(self, instance, data):
        save = False
        if data['byline']:
            instance.author = self.get_or_create_author(data['byline'].split(',')[0])
            save = True

        if save:
            instance.save()

        return instance
