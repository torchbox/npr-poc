# NPR RSS Importer

Collect realistic data from NPR.org. Expects two settings as environment variables or in `local.py`:

```python
IMPORT_ROOT_PATH = "/root/to/path/where/downloads/are/stored"
NEWS_PARENT_ID = "<id of page where news items are imported under>"
```

## Scrape 10000 stories from the RSS feed(s)

`./manage.py news_download 10000`

This downloads news stories as XML files from the NPR RSS feed, in batches of 50 items.

To save future downloads, zip the downloaded files (`zip archive.zip *.xml`) and upload the archive to a publicly available URL. This can be fetched from other machines, e.g. Heroku with `./manage.py fetch_export <URL>`.

## Import into Wagtail stories

`./manage.py news_import`

## Delete all imported news stories

```python
from npr_poc.news.models import NewsPage
for f in NewsPage.objects.all(): f.delete()
```