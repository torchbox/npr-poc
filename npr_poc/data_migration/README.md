Data migration
==============

The data migration app contains classes and utilities for importing data into
Wagtail.

The `importers/base.py` file contains base importer clasess with utilities for
formating and importing page and non-page data. Child classes inherit from
these, provide a couple of class variables and optionally override the
`format_data()` method to add to the basic set of core fields, depending
on whats available in the source data. The `create_content_item()` method
creates pages in the database, so extending this may also be required depending
on content. See example news importer.

Imports are run via management commands, see the existing folder for examples.
They are run by providing the the name of the source data file and the id of
the parent page. The data file needs to be uploaded to a location that the
server can access them. By default the commands will look for files relative to
`manage.py`. An example of running an import command using a file is:

`./manage.py import_news 4 npr_poc/data_migration/data/news.json`

Note: In the above example, 4 is the `parent_page_id` argument  


The import can be run on Heroku using local json files like so:
```bash
cat npr_poc/data_migration/data/news.json | heroku run -a npr-poc --no-tty ./manage.py import_news 4 -
```

