from django.apps import apps
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import defaults
from django.views.generic import TemplateView, View

from wagtail.admin.forms.search import SearchForm
from wagtail.contrib.modeladmin.views import ChooseParentView


def page_not_found(request, exception, template_name='patterns/pages/errors/404.html'):
    return defaults.page_not_found(request, exception, template_name)


def server_error(request, template_name='patterns/pages/errors/500.html'):
    return defaults.server_error(request, template_name)
