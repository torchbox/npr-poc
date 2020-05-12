from django.contrib import admin
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail.contrib.modeladmin.helpers import PageButtonHelper
from .models import Show, Episode


class ShowButtonHelper(PageButtonHelper):
    def view_episodes(self, pk, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.edit_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            "url": "/admin/podcasts/episode/?show=%s" % pk,
            "label": "View Episodes",
            "classname": cn,
            "title": "View Episodes",
        }

    def get_buttons_for_obj(
        self, obj, exclude=None, classnames_add=None, classnames_exclude=None
    ):
        button_list = super().get_buttons_for_obj(
            obj, exclude, classnames_add, classnames_exclude
        )
        button_list.append(
            self.view_episodes(obj.pk, classnames_add, classnames_exclude)
        )
        return button_list


class ShowFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "Show"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "show"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        # TODO get a limited set, e.g. 10 most recently edited shows
        # could restrict by request.user permissions
        print(request.user)
        return tuple(Show.objects.live().values_list("id", "title"))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            show = Show.objects.get(id=self.value())
            return queryset.child_of(show)
        else:
            return queryset


class ShowPageAdmin(ModelAdmin):
    model = Show
    menu_label = "Shows"
    menu_icon = "fa-podcast"
    list_display = ("title", "date_created", "is_explicit")
    list_export = ("title", "date_created", "is_explicit")
    list_filter = ("date_created", "is_explicit")
    search_fields = ("title",)
    button_helper_class = ShowButtonHelper


class EpisodeAdmin(ModelAdmin):
    model = Episode
    menu_label = "Episodes"
    menu_icon = "fa-microphone"
    list_display = ("title", "date_created", "episode_type", "show")
    list_export = ("title", "date_created", "episode_type", "show")
    list_filter = (ShowFilter, "date_created", "episode_type")
    search_fields = ("title",)


class TaxonomyGroup(ModelAdminGroup):
    menu_label = "Podcasts"
    menu_icon = "fa-podcast"
    menu_order = 300
    items = (ShowPageAdmin, EpisodeAdmin)


modeladmin_register(TaxonomyGroup)
