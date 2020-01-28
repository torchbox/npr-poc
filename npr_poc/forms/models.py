from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django import forms
from django.shortcuts import render

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (FieldPanel, FieldRowPanel,
                                         InlinePanel, MultiFieldPanel)
from wagtail.contrib.forms.models import AbstractForm, AbstractFormField
from wagtail.core.fields import RichTextField
from wagtail.search import index

from wagtailcaptcha.models import WagtailCaptchaEmailForm

from npr_poc.utils.models import BasePage, SkyAPISettings

from skyapi.utils import add_constituent


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


class ConstituentForm(forms.Form):
    title = forms.ChoiceField(choices=[
        ('Miss','Miss'),
        ('Mr','Mr'),
        ('Mrs','Mrs'),
        ('Ms','Ms'),
        ('Prof','Prof'),
        ])
    first_name = forms.CharField(label='First name')
    last_name = forms.CharField(label='Last name')
    email = forms.EmailField(label='Email')
    phone_number = forms.CharField(label="Phone number")
    phone_number_type = forms.ChoiceField(choices=[
        ("Mobile","Mobile"),
        ("Home","Home"),
        ("Business","Business"),
    ])
    address_line_one = forms.CharField(label="Address line one, E.G 123 Main street")
    city = forms.CharField(label="City")
    county = forms.CharField(label="County")
    postal_code = forms.CharField(label="Postcode")
    country = forms.CharField(label="Country")



class ConstituentFormPage(BasePage):
    template = 'patterns/pages/forms/form_page_renxt.html'
    landing_page_template = 'patterns/pages/forms/form_page_renxt_landing.html'

    introduction = models.TextField(blank=True)
    action_text = models.CharField(max_length=32, blank=True, help_text="Form action text. Defaults to \"Submit\"")

    content_panels = BasePage.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('action_text'),
    ]

    def serve(self, request):
        self.form = ConstituentForm(request.POST or None)
        if request.method == 'POST' and self.form.is_valid():
            constituent_data = {
                'first_name': self.form.data.get('first_name'),
                'last_name': self.form.data.get('last_name'),
                'email': self.form.data.get('email'),
                'title': self.form.data.get('title'),
                "phone": {
                    "number": self.form.data.get('phone_number'),
                    "type": self.form.data.get('phone_number_type'),
                },
                "address": {
                    "address_lines": self.form.data.get('address_line_one'),
                    "city": self.form.data.get('city'),
                    "county": self.form.data.get('county'),
                    "postal_code": self.form.data.get('postal_code'),
                    "country": self.form.data.get('country'),
                    "type": "Home",
                }
            }


            access_token = SkyAPISettings.for_site(request.site).access_token
            res = add_constituent(constituent_data, access_token)

            if not res.ok:
                print(res)
            else:
                context = self.get_context(request)
                context['constituent_id'] = res.json()['id']
                return render(request, self.landing_page_template, context)

        return super().serve(request)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)

        context['form'] = self.form
        return context
