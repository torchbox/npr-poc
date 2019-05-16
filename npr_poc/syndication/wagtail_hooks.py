from django.shortcuts import render
from django.urls import path, re_path
from django.utils.text import slugify

from wagtail.admin.action_menu import PageActionMenu
from wagtail.admin.views.pages import get_valid_next_url_from_request
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
)
from wagtail.core import hooks

from . import models, views
from .utils import get_story


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path(
            "choose-syndicated-content/",
            views.ChooseSyndicatedContentView.as_view(),
            name="npr_syndication_choose_content"
        ),
        re_path(
            "chosen-syndicated-content/([^/]+)/",
            views.ChosenSyndicatedContentView.as_view(),
            name="npr_syndication_chosen_content"
        ),
        path(
            "browse-syndicated-content/",
            views.BrowseSyndicatedContentView.as_view(),
            name="npr_syndication_browse",
        ),
        path(
            "search-syndicated-content/",
            views.SyndicatedContentSearchView.as_view(),
            name="npr_syndication_search",
        ),
    ]


class SyndicatedNewsAdmin(ModelAdmin):
    model = models.SyndicatedNewsPage
    menu_label = "Syndicated News"
    menu_icon = "fa-quote-left"  # change as required
    menu_order = 210
    exclude_from_explorer = False
    list_display = ("title", "date")
    list_filter = ("date",)
    search_fields = ("title", "date")
    choose_parent_view_class = views.SyndicatedContentChooseParentView
    index_template_name = 'modeladmin/syndicated_news_index.html'


modeladmin_register(SyndicatedNewsAdmin)


@hooks.register("before_create_page")
def create_syndicated_content(request, parent_page, page_class):
    if "story" in request.GET and request.method == "GET":
        story = get_story(request.GET['story'])
        if not story:
            return

        page = page_class(
            title=story['title'], story=story['id'], slug=slugify(story['title']), owner=request.user
        )
        edit_handler = page_class.get_edit_handler()
        edit_handler = edit_handler.bind_to(request=request, instance=page)
        form_class = edit_handler.get_form_class()

        next_url = get_valid_next_url_from_request(request)

        form = form_class(instance=page, parent_page=parent_page)
        has_unsaved_changes = False

        edit_handler = edit_handler.bind_to(form=form)

        return render(
            request,
            "wagtailadmin/pages/create.html",
            {
                "content_type": page.content_type,
                "page_class": page_class,
                "parent_page": parent_page,
                "edit_handler": edit_handler,
                "action_menu": PageActionMenu(
                    request, view="create", parent_page=parent_page
                ),
                "preview_modes": page.preview_modes,
                "form": form,
                "next": next_url,
                "has_unsaved_changes": has_unsaved_changes,
            },
        )
