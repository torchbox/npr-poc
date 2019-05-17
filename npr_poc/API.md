# API

See `api.py` for the available endpoints.

The Wagtail API uses [Django Rest Framework](https://django-rest-framework.org) (DRF) and is read-only out of the box.
It also has a browsable version.

## Storify Endpoint

The Storify endpoint is a custom, write-enabled endpoint that allows creating simple `NewsPage` objects.

You can access it at `/api/storify/`.

To create a new item:

```bash
curl -X POST \
  http://npr-poc.torchbox.com/api/storify/ \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "title": "Foo 1",
    "date": "2019-05-16",
    "body": "<h2>title me this</h2><p>something</p><ul><li>one</li><li>two</li></ul>",
    "summary": "Summary be here",
    "author": "John Doe"
}'
```
