from wagtail_content_import.mappers.converters import BaseConverter, ImageConverter, RichTextConverter, TextConverter
from wagtail_content_import.mappers.streamfield import StreamFieldMapper


class ImageBlockConverter(BaseConverter):
    image_converter = ImageConverter('')

    def __call__(self, element, user, **kwargs):
        _, image = self.image_converter(element, user=user, **kwargs)
        return (self.block_name, {'caption': '', 'image': image})


class StoryMapper(StreamFieldMapper):
    html = RichTextConverter('paragraph')
    image = ImageBlockConverter('image')
    heading = TextConverter('heading')
