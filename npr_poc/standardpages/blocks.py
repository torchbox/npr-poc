from wagtail.core import blocks

from wagtailnhsukfrontend.blocks import DoBlock, DontBlock, InsetTextBlock

from npr_poc.utils.blocks import ImageBlock, QuoteBlock


class HealthStoryBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(
        classname='full title', icon='title',
        template='patterns/molecules/streamfield/blocks/heading_block.html'
    )
    paragraph = blocks.RichTextBlock()
    image = ImageBlock()
    quote = QuoteBlock()

    # Blocks provided by NHS service manual
    # https://github.com/nhsuk/wagtail-nhsuk-frontend
    do_block = DoBlock()
    dont_block = DontBlock()
    inset_text = InsetTextBlock()

    class Meta:
        template = "patterns/molecules/streamfield/stream_block.html"
