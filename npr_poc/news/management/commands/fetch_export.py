import requests, zipfile, io
from django.conf import settings
from django.core.management.base import BaseCommand

NPR_EXPORT_URL = "https://tom.s3.amazonaws.com/test.zip"


class Command(BaseCommand):
    help = "Fetch and unzip zip file of RSS export"

    def handle(self, *args, **options):
        response = requests.get(NPR_EXPORT_URL)
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(path=settings.IMPORT_ROOT_PATH)
        print(f"unzipped to {settings.IMPORT_ROOT_PATH}")
