import json
from datetime import datetime

import pytz
from django.utils import timezone

from npr_poc.news.models import NewsPage, Author, NewsCategory, NewsPageNewsCategory, NewsPageTag
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
        ('legacy_id', legacy_id_field, None),
        ('date', 'first_published_at', None),
        ('first_published_at', 'first_published_at', None)
    )
    timezone = pytz.timezone('US/Eastern')
    description = "News Page"

    def format_data(self, data):
        """ Overridden to add a body field """
        formatted_data = super().format_data(data)

        body = data['body']
        if data.get('image_gallery'):
            body = data['image_gallery'] + body

        body = html_to_stream_data(body)
        formatted_data['body'] = json.dumps(body)

        date = self.get_date(formatted_data, 'date')
        formatted_data['date'] = date.strftime('%Y-%m-%d')
        formatted_data['first_published_at'] = self.get_date(formatted_data, 'first_published_at')

        return formatted_data

    def get_or_create_author(self, author_name):
        try:
            author = Author.objects.get(name=author_name)
        except Author.DoesNotExist:
            author = Author(name=author_name)
            author.save()
        return author

    def add_category(self, instance, category):
        try:
            category = NewsCategory.objects.get(name=category)
        except NewsCategory.DoesNotExist:
            category = NewsCategory(
                name=category,
                slug=self.get_slug_from_title(category)
            )
            category.save()

        if not NewsPageNewsCategory.objects.filter(page=instance, category=category).exists():
            category_to_page = NewsPageNewsCategory(
                page=instance,
                category=category
            )
            category_to_page.save()

        return category

    def post_process(self, instance, data):
        save = False
        if data['byline']:
            instance.author = self.get_or_create_author(data['byline'].split(',')[0])
            save = True

        if data['category']:
            self.add_category(instance, data['category'])

        if save:
            instance.save()

        return instance
