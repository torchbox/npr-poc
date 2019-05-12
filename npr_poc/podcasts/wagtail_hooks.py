from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Show


class ShowPageAdmin(ModelAdmin):
    model = Show
    menu_label = "Podcasts"
    menu_icon = "pilcrow"
    menu_order = 300
    exclude_from_explorer = False
    list_display = ("title", "date_created")
    list_filter = ("date_created",)
    search_fields = ("title",)


modeladmin_register(ShowPageAdmin)
