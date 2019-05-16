import json
from argparse import ArgumentTypeError

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.utils.module_loading import import_string

from npr_poc.data_migration.tasks import import_from_url
from npr_poc.data_migration.utils import LineBreakWriter, is_valid_url


def email_type(recipient):
    try:
        validate_email(recipient)
    except ValidationError:
        raise ArgumentTypeError(f"'{recipient}' is not a valid email address")
    return recipient


class BaseImporterCommand(BaseCommand):
    """
    Base class for importing from a file into Django using importer classes
    and a JSON source data file.
    """
    importer = None

    def add_arguments(self, parser):
        parser.add_argument('source', help='Migration source JSON file')
        parser.add_argument('--reimport', action='store_true',
                            help='Overwrite existing records')
        parser.add_argument('--outfile', help='File for output, instead of stdout')
        parser.add_argument('--recipients', nargs='+', metavar='RECIPIENT',
                            type=email_type,
                            help="Sends the output as an email attachment to "
                            "the addresses given. Separate with spaces.")
        parser.add_argument('--stoppage', type=int,
                            help='Maximum page number to import')
        parser.add_argument('--synchronous', action='store_true',
                            help='Run synchronously.')
        parser.add_argument('--plaintext', action='store_true',
                            help='Do not encrypt log.')

    def handle(self, *args, **options):
        """
        Run the import.
        """

        if options['recipients']:
            if options['outfile']:
                raise CommandError("The 'recipients' and 'outfile' options "
                                   "cannot be used together.")

        if options['plaintext']:
            answer = input("Warning: only use the plaintext option in testing. "
                           "Continue? (y/n) ")
            if answer.lower() != 'y':
                raise CommandError("That was lucky.")

        if not is_valid_url(options['source']):
            self.import_from_file(options)
            return

        importer_options = self.get_importer_options(**options)

        import_from_url(
            self.importer_class, importer_options, **options
        )
        self.stdout.write('Done!')

    def import_from_file(self, options):
        data = self._get_source_data_from_file(options['source'])

        importer_options = self.get_importer_options(**options)
        if options['outfile']:
            importer_options['stdout'] = LineBreakWriter(self.outfile)
        else:
            importer_options['stdout'] = LineBreakWriter(self.stdout)

        importer_class = import_string(self.importer_class)
        self.importer = importer_class(data, **importer_options)

        if options.get('parent_page_id'):
            self.importer.parent_page = self.importer.parent_page_model.objects.get(
                id=options['parent_page_id']
            )

        self.importer.process()

    def _get_source_data_from_file(self, source):
        if source.endswith(".csv"):
            return self._get_source_data_from_csv(source)
        elif source.endswith(".xml"):
            return self._get_source_data_from_xml(source)

        with open(source, 'rb') as f:
            data = f.read()

        return json.loads(data)

    def get_importer_options(self, **options):
        return {
            'reimport': options['reimport'],
            'verbosity': options['verbosity'],
            'plaintext': options['plaintext'],
        }

    def _get_source_data_from_xml(self, source):
        import xml.etree.ElementTree as ET
        tree = ET.parse(source)
        nodes = tree.getroot()

        items = []
        for node in nodes:
            d = {child.tag: child.text for child in node}
            items.append(d)

        return items

    def _get_source_data_from_csv(self, source):
        with open(source, 'r') as f:
            import csv
            reader = csv.DictReader(f)
            data = [row for row in reader]
        return data


class BasePageImporterCommand(BaseImporterCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'parent_page_id',
            help='The ID of the page to import the files under'
        )
        super().add_arguments(parser)

