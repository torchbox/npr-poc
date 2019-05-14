from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from .models import Show, Episode


class ShowPageAdmin(ModelAdmin):
    model = Show
    menu_label = "Shows"
    menu_icon = "fa-podcast"
    list_display = ("title", "date_created", "is_explicit")
    list_filter = ("date_created", "is_explicit")
    search_fields = ("title",)


class EpisodeAdmin(ModelAdmin):
    model = Episode
    menu_label = "Episodes"
    menu_icon = "fa-microphone"
    list_display = ("title", "date_created", "episode_type", "show")
    list_filter = ("date_created", "episode_type")
    search_fields = ("title",)


class TaxonomyGroup(ModelAdminGroup):
    menu_label = "Podcasts"
    menu_icon = "fa-podcast"
    menu_order = 300
    items = (ShowPageAdmin, EpisodeAdmin)


modeladmin_register(TaxonomyGroup)
