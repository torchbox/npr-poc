from django.apps import apps
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import defaults
from django.views.generic import TemplateView, View

from wagtail.admin.forms.search import SearchForm
from wagtail.contrib.modeladmin.views import ChooseParentView

from .google import (get_auth_url, save_access_tokens_to_session,
                     search_documents)


def page_not_found(request, exception, template_name='patterns/pages/errors/404.html'):
    return defaults.page_not_found(request, exception, template_name)


def server_error(request, template_name='patterns/pages/errors/500.html'):
    return defaults.server_error(request, template_name)


def request_google_oauth(request):
    return HttpResponseRedirect(get_auth_url())


def process_google_oauth(request):
    if request.GET.get('error'):
        # TODO add error handling
        pass
    else:
        save_access_tokens_to_session(request, '/')

    # Check if the session tells us where to redirect to
    return HttpResponseRedirect(request.session.get('oauth_complete_redirect_uri', '/'))


class PageFromGoogleDocChooserView(TemplateView):
    template_name = 'wagtailadmin/pages/add_subpage_from_google.html'

    def get(self, request, *args, **kwargs):
        if 'google_oauth_credentials' not in request.session:
            request.session['oauth_complete_redirect_uri'] = request.get_full_path()
            return HttpResponseRedirect(reverse('npr_utils_google_oauth'))
        return super().get(request, *args, *kwargs)

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(
            reverse(
                'wagtailadmin_pages:add',
                args=(kwargs['app_label'], kwargs['model_name'], kwargs['parent_page_id'])
            ) + '?google-doc-id={}'.format(request.POST['docid'])
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        docs = search_documents(self.request.session['google_oauth_credentials'], q=self.request.GET.get('q'))
        ctx['documents'] = docs
        ctx['search_form'] = SearchForm(self.request.GET or None, placeholder='Search for documents')
        return ctx


class PageFromGoogleDocSearchView(View):

    def get(self, request, *args, **kwargs):
        # TODO handle missing credentials
        docs = search_documents(self.request.session['google_oauth_credentials'], q=request.GET.get('q'))
        return render(request, 'wagtailadmin/pages/google_doc_results.html', {
            'documents': docs,
            'query_string': request.GET.get('q'),
        })


class GoogleImportChooseParentView(ChooseParentView):
    """
    Custom ChooseParentView that allows the option to create a page from Google Doc.
    """
    def form_valid(self, form):
        if self.request.POST.get('google-doc-import'):
            return redirect(
                'npr_utils_page_from_google_doc',
                self.app_label, self.model_name, form.cleaned_data['parent_page'].pk
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'app_label': self.app_label,
            'model_name': self.model_name,
        })
        return ctx
