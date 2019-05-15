from npr_poc.news.models import NewsPage, Author
from npr_poc.utils.google import html_to_stream_data

from .base import BaseImporter


class NewsImporter(BaseImporter):
    """
    Example use of the BasePageImporter for importing a specific page type
    """

    content_model = NewsPage
    legacy_id_field = 'nid'
    source_str_field = 'title'
    imported_str_field = 'slug'
    expected_source_data_type = dict
    field_mapping = (
        # local key, import key, truncation length
        ('title', 'news_item_title', 255),
        ('summary', 'summary', None),
        ('body', 'body', None),
        ('legacy_id', legacy_id_field, None),
        ('date', 'first_published_at', None),
    )
    description = "News Page"

    def format_data(self, data):
        """ Overridden to add a body field """
        formatted_data = super().format_data(data)

        formatted_data['body'] = html_to_stream_data(formatted_data['body'])

        return formatted_data

    def get_or_create_author(self, author_name):
        try:
            author = Author.objects.get(name=author_name)
        except Author.DoesNotExist:
            author = Author(name=author_name)
            author.save()
        return author

    def post_process(self, instance, data):
        if not data.get['field_people']:
            return

        for person in data['field_people'].items():
            instance.author = self.get_or_create_author(person)

        instance.save()

        return instance
