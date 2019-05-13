import requests
import os
from django.conf import settings
from django.core.management.base import BaseCommand

PAGE_SIZE = 50
NEWS_RSS_ROOT = f"https://www.npr.org/rss/rss.php?id=1001&numResults={PAGE_SIZE}"
IMPORT_ROOT_PATH = settings.IMPORT_ROOT_PATH


class Command(BaseCommand):
    help = "Download everything"

    def add_arguments(self, parser):
        parser.add_argument(
            "total",
            type=int,
            help="Number of items to import (multiple of 50)",
            default=100,
        )

    def handle(self, *args, **options):
        total = options["total"]
        start_at = 0
        while start_at < total:
            up_to = start_at + PAGE_SIZE
            output_file = f"{IMPORT_ROOT_PATH}/news-{start_at}-{up_to}.xml"
            if os.path.isfile(output_file):
                print("found " + output_file + ", skipping")
            else:
                response = requests.get(f"{NEWS_RSS_ROOT}&startNum={start_at}")
                file = open(output_file, "w")
                file.write(response.text)
                file.close()
                print("created " + output_file)
            start_at += PAGE_SIZE
