import uuid

from django.core.files.base import ContentFile
from django.utils.text import slugify

from bs4 import BeautifulSoup, NavigableString
import requests
from requests.exceptions import MissingSchema

from npr_poc.images.models import CustomImage


def create_streamfield_block(**kwargs):
    # Add an ID to the block, because wagtail-react-streamfield borks without one
    kwargs['id'] = str(uuid.uuid4())
    return kwargs


def close_paragraph(block, stream_data):
    if block:
        stream_data.append(create_streamfield_block(type='paragraph', value=''.join(block)))
    block.clear()


def import_image(img_tag):
    if not img_tag.get('src') or '/tracking/' in img_tag['src'] or '__utm.gif' in img_tag['src']:
        return

    try:
        response = requests.get(img_tag['src'])
    except MissingSchema:
        return

    if not response.status_code == 200:
        return

    img_content = response.content
    img_title = img_tag.get('alt', '')
    img_file_name = slugify(img_title) if img_title else uuid.uuid4()
    img_content_type = response.headers.get('Content-Type', '')
    if img_content_type.startswith('image/'):
        # TODO we probably want to be a lot more discriminating here
        file_extension = img_content_type.split('/')[1]
    else:
        # Don't mess with what isn't an image
        return

    img_file_name = '{}.{}'.format(img_file_name, file_extension)

    # Create the image
    image = CustomImage(
        title=img_title or img_file_name,
    )

    image.file.save(img_file_name, ContentFile(response.content))
    image.save()
    return image


def html_to_stream_data(html):
    soup = BeautifulSoup(html)

    stream_data = []

    # Run through contents and populate stream
    current_paragraph_block = []

    for tag in soup.body.recursiveChildGenerator():
        # Remove all inline styles and classes
        if hasattr(tag, 'attrs'):
            for attr in ['class', 'style']:
                tag.attrs.pop(attr, None)

    for tag in soup.body.contents:
        if isinstance(tag, NavigableString):
            stream_data.append(create_streamfield_block(type='paragraph', value=str(tag)))
        else:
            if tag.name == 'h1':
                close_paragraph(current_paragraph_block, stream_data)
                # Wagtail will render this as a h2
                stream_data.append(create_streamfield_block(type='heading', value=tag.text))
            elif tag.name == 'h2':
                close_paragraph(current_paragraph_block, stream_data)
                # h2 > h3
                current_paragraph_block = ['<h3>{}</h3>'.format(tag.text)]
            elif tag.name in ['h3', 'h4', 'h5', 'h6']:
                # Rich text field only allows h3 and h4 by default, so we just set to h4
                current_paragraph_block.append('<h4>{}</h4>'.format(tag.text))
            elif tag.name == 'img':
                image = import_image(tag)
                if image:
                    # Break the paragraph and add an image
                    close_paragraph(current_paragraph_block, stream_data)
                    stream_data.append(create_streamfield_block(type='image', value={'image': image.pk}))
            elif tag.text:
                current_paragraph_block.append(str(tag))

            if tag.find_all('img'):
                # Break the paragraph and add images
                close_paragraph(current_paragraph_block, stream_data)
                for img in tag.find_all('img'):
                    image = import_image(img)
                    if image:
                        stream_data.append(create_streamfield_block(type='image', value={'image': image.pk}))

    close_paragraph(current_paragraph_block, stream_data)

    return stream_data
