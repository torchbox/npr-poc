# NPR RSS Importer

Collect realistic data from NPR.org

 - Scrape stories from the RSS feed(s)
 - Import into Wagtail stories

 ```
from npr_poc.news.models import NewsPage
np = NewsPage.objects.all()
for f in np: f.delete()
```