from django.apps import apps
from django import template

from wagtail.core.utils import camelcase_to_underscore

from npr_poc.utils.models import SocialMediaSettings

register = template.Library()


# Social text
@register.filter(name='social_text')
def social_text(page, site):
    try:
        return page.social_text
    except AttributeError:
        return SocialMediaSettings.for_site(site).default_sharing_text


# Get widget type of a field
@register.filter(name='widget_type')
def widget_type(bound_field):
    return camelcase_to_underscore(bound_field.field.widget.__class__.__name__)


# Get type of field
@register.filter(name='field_type')
def field_type(bound_field):
    return camelcase_to_underscore(bound_field.field.__class__.__name__)


@register.simple_tag
def can_import_from_google(app_label, model_name):
    model = apps.get_model(app_label, model_name)
    return getattr(model, 'can_import_from_google', False)
