from wagtail_content_import.mappers.converters import BaseConverter, ImageConverter, RichTextConverter, TextConverter
from wagtail_content_import.mappers.streamfield import StreamFieldMapper


class ImageBlockConverter(BaseConverter):
    def __call__(self, element, user, *args, **kwargs):
        image_url = element['value']
        image_name, image_content = ImageConverter.fetch_image(image_url)
        image = ImageConverter.import_as_image_model(image_name, image_content, owner=user)
        return (self.block_name, {'caption': '', 'image': image})


class StoryMapper(StreamFieldMapper):
    html = RichTextConverter('paragraph')
    image = ImageBlockConverter('image')
    heading = TextConverter('heading')
