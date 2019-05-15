from ._base import BasePageImporterCommand


class Command(BasePageImporterCommand):
    """
    Example import management command to import news
    """
    importer_class = 'npr_poc.data_migration.importers.news.NewsImporter'

