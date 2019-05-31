from django.contrib.syndication.views import Feed
from django.utils import feedgenerator
from django.utils.html import strip_tags

from .utils import absurl


class PodcastFeed(feedgenerator.Rss201rev2Feed):
    def rss_attributes(self):
        attrs = super().rss_attributes()
        attrs.update(
            {
                "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
                "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
            }
        )
        return attrs

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        handler.addQuickElement("content:encoded", self.feed["description"])
        # Image for general RSS
        if self.feed["image"]:
            handler.startElement("image", {})
            # See RSS specification for max image dimensions
            handler.addQuickElement(
                "url", absurl(self.feed["image"].image.get_rendition("max-144x400").url)
            )
            handler.addQuickElement("title", self.feed["image"].image.title)
            handler.addQuickElement("link", self.feed["link"])
            handler.endElement("image")

            # Image for iTunes
            handler.addQuickElement(
                "itunes:image",
                "",
                {
                    "href": absurl(
                        self.feed["image"].image.get_rendition("max-3000x3000").url
                    )
                },
            )

        handler.addQuickElement("itunes:type", self.feed["type"])
        handler.addQuickElement("itunes:subtitle", self.feed["subtitle"])
        handler.addQuickElement("itunes:author", self.feed["author"]["name"])

        handler.startElement("itunes:owner", {})
        handler.addQuickElement("itunes:name", self.feed["owner"]["name"])
        handler.addQuickElement("itunes:email", self.feed["owner"]["email"])
        handler.endElement("itunes:owner")

        # TODO - iTunes has a specific list of categories that we need to use,
        # and it also supports nested categories.
        for cat in self.feed["categories"]:
            handler.addQuickElement("itunes:category", "", {"text": str(cat)})

        handler.addQuickElement(
            "itunes:explicit", "true" if self.feed["explicit"] else "false"
        )
        handler.addQuickElement("itunes:block", "Yes" if self.feed["block"] else "No")
        handler.addQuickElement(
            "itunes:complete", "Yes" if self.feed["complete"] else "No"
        )

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        if item["duration"]:
            # Convert to MM:SS
            h, m = divmod(item["duration"], 60)
            handler.addQuickElement("itunes:duration", "%02d:%02d" % (h, m))

        if item["image"]:
            handler.addQuickElement(
                "itunes:image",
                "",
                {
                    "href": absurl(
                        item["image"].image.get_rendition("max-3000x3000").url
                    )
                },
            )

        handler.addQuickElement(
            "itunes:explicit", "true" if item["explicit"] else "false"
        )
        handler.addQuickElement("itunes:episodeType", item["episode_type"])

        if item["season_number"]:
            handler.addQuickElement("itunes:season", item["season_number"])


class ShowFeed(Feed):

    feed_type = PodcastFeed

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def get_object(self, request, show_id):
        from .models import Show  # Avoid circular import

        return Show.objects.get(pk=show_id)

    def title(self, obj):
        return str(obj)

    def description(self, obj):
        return strip_tags(obj.description)

    def language(self, obj):
        return strip_tags(obj.language)

    def categories(self, obj):
        return obj.tags.all()

    def subtitle(self, obj):
        return obj.subtitle

    def link(self, obj):
        return obj.full_url

    def items(self, obj):
        return obj.get_children().live().specific()[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return strip_tags(item.description)

    def item_link(self, item):
        return item.full_url

    def item_enclosures(self, item):
        enclosures = []
        for enc in item.enclosures.all():
            if enc.media.file.url.startswith("http"):
                url = enc.media.file.url
            else:
                url = "{}{}".format(
                    self.request.build_absolute_uri("/").rstrip("/"), enc.media.file.url
                )
            enclosure = feedgenerator.Enclosure(
                url=url, length=str(enc.media.file.size), mime_type=enc.media.mime_type
            )
            enclosures.append(enclosure)
        return enclosures

    def item_categories(self, item):
        return item.tags.all()

    def item_pubdate(self, item):
        return item.date_created

    def item_updateddate(self, item):
        return item.date_updated

    def feed_extra_kwargs(self, obj):
        return {
            "image": obj.images.first(),
            "description_html": obj.description,
            "type": "serial"
            if obj.podcast_type == obj.SHOW_TYPE_SERLIALIZED
            else "episodic",
            # TODO these have specific meanings - owner is the adminstrator of the podcast
            "author": {
                "name": obj.owner.get_full_name() if obj.owner else "",
                "email": obj.owner.email if obj.owner else "",
            },
            "owner": {
                "name": obj.owner.get_full_name() if obj.owner else "",
                "email": obj.owner.email if obj.owner else "",
            },
            "explicit": obj.is_explicit,
            "block": False,
            "complete": False,
        }

    def item_extra_kwargs(self, item):
        default_enclosure = item.enclosures.first()
        return {
            "duration": default_enclosure.media.duration if default_enclosure else None,
            "image": item.images.first(),
            "explicit": item.is_explicit,
            "season_number": item.season_number,
            "episode_type": item.episode_type,
        }
