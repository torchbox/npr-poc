import os
import sys
from datetime import datetime
from html import unescape
from urllib import parse

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify


class PageTypeException(TypeError):
    pass


class SourceDataException(TypeError):
    pass


class BaseImporter(object):
    """
    Base class containing utilities for creating content-specific importers.

    Subclass to create base classes for content-specific imports, e.g.
    BasePageImporter for pages.

    Subclasses will mainly override 'format_page_data()' to map the required
    data from the source file to the destination content fields. To customise
    the creation of the object override 'create_content_item()'.

    Class attributes:
        - content_model: the class of the content to be imported.
        - timezone: the timezone to use for formatting dates
        - legacy_id_field: the source field to store as the imported legacy_id
        - expected_source_data_type
        - source_str_field: the name of the source field to use in command
          reporting output
        - imported_str_field: the name of the destination field to use in
          command reporting output
        - field_mapping: an iterable of 2-tuples (local_key, import_key) to map
          directly, applying only the self.clean_text() method
        - reimport: determines whether to update existing records

    Instance attributes:
        - source_data: the JSON source data.
        - import_count: running total of imported items.

    """
    content_model = None
    timezone = timezone.utc
    legacy_id_field = 'nid'
    expected_source_data_type = list
    source_str_field = 'title'
    imported_str_field = 'title'
    field_mapping = (
        ('legacy_id', legacy_id_field, None),
    )

    def __init__(self, source_data, reimport=False, plaintext=False, stdout=sys.stdout, verbosity=1):
        if not isinstance(source_data, self.expected_source_data_type):
            raise SourceDataException(
                f'Source data is not {self.expected_source_data_type}, is {source_data.__class__}'
            )
        self.source_data = source_data
        self.import_count = 0
        self.reimport = reimport
        self.stdout = stdout
        self.verbosity = verbosity
        self.plaintext = plaintext

    def format_data(self, data):
        """
        Format the basic fields for the content. Extend in child classes for
        more fields.
        """
        return {key: self.clean_text(self.get_value(data, import_key), length)
                for key, import_key, length in self.field_mapping}

    def process(self):
        """
        Call from external code to run the import with the supplied source data
        """
        for data in self.get_iterator():
            try:
                formatted_data = self.format_data(data)

                # formatted_data['imported_at'] = timezone.localtime(timezone=self.timezone)

                try:
                    instance = self.content_model.objects.get(
                        legacy_id=self.get_value(data, self.legacy_id_field)
                    )
                    created = False
                except self.content_model.DoesNotExist:
                    instance = None
                    created = True  # well… it will be shortly

                if instance and not self.reimport:
                    if self.verbosity > 1:
                        self.stdout.write(f"{self.legacy_id_field} {self.get_value(data, self.legacy_id_field)} already exists")
                    continue

                try:
                    instance = self.create_content_item(formatted_data, instance)
                except Exception as e:
                    msg = f"Could not import record with {self.legacy_id_field} {self.get_value(data, self.legacy_id_field)}, {self.get_value(data, self.source_str_field)}: {e}"
                    self.stdout.write(msg)
                    continue

                if self.verbosity > 1:
                    if created:
                        self.stdout.write(f'Created {self.get_imported_str(instance)}')
                    else:
                        self.stdout.write(f'Reimported {self.get_imported_str(instance)}')

                instance = self.post_process(instance, data)

            except ValidationError as e:
                msg = f"Could not import record with {self.legacy_id_field} {self.get_value(data, self.legacy_id_field)}, {self.get_value(data, self.source_str_field)}: {e}"
                self.stdout.write(msg)

    def get_imported_str(self, instance):
        """ Return the string representation of the ipmorted record.

        Used for import command output. Takes the instance as an argument to
        make overriding flexible.
        """
        return getattr(instance, self.imported_str_field)

    def create_content_item(self, data, instance=None):
        """ Create or update the content item """
        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
        else:
            instance = self.content_model(**data)

        instance.save()
        return instance

    def get_iterator(self):
        return self.source_data

    def get_value(self, data, value):
        """
        Get the value from the source data. Override as required to customise
        for source data format.
        """
        return data[value]

    def clean_text(self, value, length=None):
        """ Clean a char or text field, trimming to length if provided """
        value = unescape(strip_tags(value).strip())
        if length is not None:
            return value[:int(length)]
        return value

    def get_date(self, data, date_field):
        return self._format_date(self.get_value(data, date_field))

    def _format_date(self, date):
        """ Format the supplied date for Django datetime field """
        return timezone.make_aware(
            datetime.strptime(date, "%Y-%m-%d %H:%M:%S"), self.timezone
        )

    def _filename_from_url(self, url):
        url_parsed = parse.urlparse(url)
        return os.path.split(url_parsed.path)[1]

    def post_process(self, instance, data):
        return instance


class BasePageImporter(BaseImporter):

    parent_page = None

    def format_data(self, data):
        """
        Format the basic page fields. Extend in child classes for more fields.
        Amend keys as required.
        """
        formatted_data = super().format_data(data)

        slug = self.get_slug_from_title(data['title'])

        formatted_data.update({
            'slug': slug,
        })
        return formatted_data

    def create_content_item(self, data, page=None):
        """ Create a page content item """
        """ Create or update the content item """
        if page:
            for key, value in data.items():
                setattr(page, key, value)
        else:
            page = self.content_model(**data)

            # Add page to parent
            self.parent_page.add_child(instance=page)

        # Save a revision
        revision = page.save_revision()
        revision.publish()

        # create a redirect
        # self.create_redirect(page)

        return page

    def get_slug_from_data(self, data, slug_field):
        return self._find_available_page_slug(
            self.get_value(data, slug_field), self.parent_page
        )

    def get_slug_from_url(self, url):
        """ Return the slug from the supplied URL """
        parsed_url = parse.urlparse(url)
        path = parsed_url.path
        path_components = [
            component for component in path.split('/') if component
        ]
        requested_slug = slugify(parse.unquote(path_components[-1]))
        return self._find_available_page_slug(requested_slug, self.parent_page)

    def get_slug_from_title(self, title):
        return self._find_available_page_slug(slugify(title), self.parent_page)

    def _find_available_page_slug(self, requested_slug, parent_page):
        """ Find a slug for page content type. """
        existing_slugs = set(parent_page.get_children().filter(
            slug__startswith=requested_slug).values_list('slug', flat=True))
        slug = requested_slug
        number = 1

        while slug in existing_slugs:
            slug = requested_slug + '-' + str(number)
            number += 1

        return slug
