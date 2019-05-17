from collections import OrderedDict

from django import forms
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, View

from wagtail.admin.forms.search import SearchForm
from wagtail.contrib.modeladmin.views import ChooseParentView

from generic_chooser.views import ChooseView, ChosenView

from .utils import get_story, render_snippet, search_stories, story_to_dict


# Hard-coded list of stations, for demo purposes
ORGS = OrderedDict([
    ('1', 'NPR'),
    ('552', 'WNYC'),
    ('704', 'WGUC'),
    ('4788725', 'American Public Media'),
    ('172', 'Jefferson PUblic Radio'),
    ('156', 'Northwest Public Radio'),
])


class ChooseSyndicatedContentView(ChooseView):
    icon = 'page'
    page_title = _("Choose content from NPR")
    choose_url_name = 'npr_syndication_choose_content'
    chosen_url_name = 'npr_syndication_chosen_content'
    is_searchable = True

    per_page = 25

    def get_object_list(self):
        search_term = self.search_query or ''
        return search_stories(search_term)

    def get_object_string(self, item):
        return '{} ({})'.format(item.title.text, item.organization.find('name').text)

    def get_object_id(self, item):
        return item['id']


class ChosenSyndicatedContentView(ChosenView):

    def get_object(self, pk):
        return get_story(pk)

    def get_object_id(self, instance):
        return instance['id']

    def get_object_string(self, instance):
        return render_snippet(instance)

    def get_response_data(self, item):
        data = super().get_response_data(item)
        data['slug'] = slugify(item['title'])
        return data


class BrowseSyndicatedContentView(TemplateView):
    model_admin = None
    template_name = 'wagtailadmin/pages/browse_syndicated_content.html'

    def __init__(self, model_admin=None):
        super().__init__()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q')
        stories = search_stories(search_term=search_query, org=self.request.GET.get('org'))
        ctx['stories'] = [story_to_dict(story) for story in stories]
        ctx['search_form'] = SearchForm(self.request.GET if search_query else None, placeholder='Search for a story, podcast or station')
        ctx['orgs'] = ORGS
        ctx['selected_org'] = self.request.GET.get('org', '')
        return ctx

    @property
    def media(self):
        return forms.Media(css={'all': ['wagtailmodeladmin/css/index.css']})


class SyndicatedContentSearchView(View):

    def get(self, request, *args, **kwargs):
        stories = search_stories(search_term=request.GET.get('q'), org=request.GET.get('org'))
        return render(request, 'wagtailadmin/pages/syndicated_content_results.html', {
            'stories': [story_to_dict(story) for story in stories],
            'query_string': request.GET.get('q'),
        })


class SyndicatedContentChooseParentView(ChooseParentView):

    def form_valid(self, form):
        parent_pk = form.cleaned_data['parent_page'].pk
        url = self.url_helper.get_action_url('add', self.app_label, self.model_name, parent_pk)
        story_id = self.request.GET.get('story')
        if story_id:
            operator = '?' if '?' not in url else '&'
            url += '{}story={}'.format(operator, story_id)
        return redirect(url)
