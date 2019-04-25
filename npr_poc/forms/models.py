from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (FieldPanel, FieldRowPanel,
                                         InlinePanel, MultiFieldPanel)
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.core.fields import RichTextField
from wagtail.search import index

from wagtailcaptcha.models import WagtailCaptchaEmailForm

from npr_poc.utils.models import BasePage


class FormField(AbstractFormField):
    page = ParentalKey('FormPage', related_name='form_fields')


# Never cache form pages since they include CSRF tokens.
@method_decorator(never_cache, name='serve')
class FormPage(WagtailCaptchaEmailForm, BasePage):
    template = 'patterns/pages/forms/form_page.html'
    landing_page_template = 'patterns/pages/forms/form_page_landing.html'

    subpage_types = []

    introduction = models.TextField(blank=True)
    thank_you_text = RichTextField(
        blank=True,
        help_text="Text displayed to the user on successful submission of the form"
    )
    action_text = models.CharField(max_length=32, blank=True, help_text="Form action text. Defaults to \"Submit\"")

    search_fields = BasePage.search_fields + [
        index.SearchField('introduction'),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel('introduction'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('action_text'),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]
