import requests
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

PAGE_SIZE = 50
TOTAL = 30000
NEWS_RSS_ROOT = f"https://www.npr.org/rss/rss.php?id=1001&numResults={PAGE_SIZE}"
IMPORT_ROOT = settings.IMPORT_ROOT


class Command(BaseCommand):
    help = "Download everything"

    def handle(self, *args, **options):
        start_at = 0
        while start_at < TOTAL:
            up_to = start_at + PAGE_SIZE
            output_file = f"{IMPORT_ROOT}/news-{start_at}-{up_to}.xml"
            if os.path.isfile(output_file):
                print("found " + output_file + ", skipping")
            else:
                response = requests.get(f"{NEWS_RSS_ROOT}&startNum={start_at}")
                file = open(output_file, "w")
                file.write(response.text)
                file.close()
                print("created " + output_file)
            start_at += PAGE_SIZE
