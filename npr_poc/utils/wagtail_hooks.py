import json

from django.shortcuts import render
from django.urls import path

from wagtail.admin.action_menu import PageActionMenu
from wagtail.admin.views.pages import get_valid_next_url_from_request
from wagtail.core import hooks

from . import views
from .google import parse_document


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('google-oauth/', views.request_google_oauth, name='npr_utils_google_oauth'),
        path('google-oauth/complete/', views.process_google_oauth, name='npr_utils_google_oauth_complete'),
        path(
            'pages/add-from-google/<str:app_label>/<str:model_name>/<int:parent_page_id>',
            views.PageFromGoogleDocChooserView.as_view(),
            name='npr_utils_page_from_google_doc'
        ),
        path(
            'pages/add-from-google/search/',
            views.PageFromGoogleDocSearchView.as_view(),
            name='npr_utils_google_doc_search'
        ),
    ]


@hooks.register('before_create_page')
def create_from_google_doc(request, parent_page, page_class):
    if 'google-doc-id' in request.GET and request.method == 'GET':
        title, body = parse_document(request.session['google_oauth_credentials'], request.GET['google-doc-id'])
        page = page_class(
            title=title,
            body=json.dumps(body),
            owner=request.user,
        )
        edit_handler = page_class.get_edit_handler()
        edit_handler = edit_handler.bind_to(request=request, instance=page)
        form_class = edit_handler.get_form_class()

        next_url = get_valid_next_url_from_request(request)

        form = form_class(instance=page, parent_page=parent_page)
        has_unsaved_changes = False

        edit_handler = edit_handler.bind_to(form=form)

        return render(request, 'wagtailadmin/pages/create.html', {
            'content_type': page.content_type,
            'page_class': page_class,
            'parent_page': parent_page,
            'edit_handler': edit_handler,
            'action_menu': PageActionMenu(request, view='create', parent_page=parent_page),
            'preview_modes': page.preview_modes,
            'form': form,
            'next': next_url,
            'has_unsaved_changes': has_unsaved_changes,
        })
