# NPR RSS Importer

Collect realistic data from NPR.org

## Scrape stories from the RSS feed(s)

`./manage.py news_download`

This downloads news stories as XML files from the NPR RSS feed, in batches of 50 items.

To save future downloads, zip the downloaded files (`zip archive.zip *.xml`) and upload the archive to a publicly available URL. This can be fetched from other machines, e.g. Heroku with `./manage.py fetch_export <URL>`.

## Import into Wagtail stories

`./manage.py news_import`

Delete all imported news stories

```
from npr_poc.news.models import NewsPage
for f in NewsPage.objects.all(): f.delete()
```