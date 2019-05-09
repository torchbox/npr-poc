from django.urls import path

from wagtail.core import hooks

from . import views


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
