import requests, zipfile, io
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Fetch and unzip zip file of RSS export"

    def add_arguments(self, parser):
        parser.add_argument("URL", type=str, help="URL of the zip to fetch")

    def handle(self, *args, **options):
        url = options["URL"]
        response = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(path=settings.IMPORT_ROOT_PATH)
        print(f"unzipped to {settings.IMPORT_ROOT_PATH}")
