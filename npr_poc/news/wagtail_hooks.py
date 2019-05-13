from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core.models import Page, PageRevision
from .models import NewsPage


class NewsPageAdmin(ModelAdmin):
    model = NewsPage
    menu_label = "News"  # ditch this to use verbose_name_plural from model
    menu_icon = "fa-quote-left"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    exclude_from_explorer = (
        False
    )  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ("title", "date", "author")
    list_filter = ("date",)
    search_fields = ("title",)


class MyPagesAdmin(ModelAdmin):
    model = Page
    menu_label = "My pages"  # ditch this to use verbose_name_plural from model
    menu_icon = "pilcrow"  # change as required
    menu_order = 150  # will put in 3rd place (000 being 1st, 100 2nd)
    exclude_from_explorer = False
    list_display = ("title", "latest_revision_created_at")
    list_filter = ("latest_revision_created_at",)
    search_fields = ("title",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show pages owned by the current user
        return qs.filter(owner=request.user)


class MyPageRevisionsAdmin(ModelAdmin):
    model = PageRevision
    menu_label = "My edits"
    menu_icon = "pilcrow"
    menu_order = 160  # (000 being 1st, 100 2nd)
    exclude_from_explorer = False
    list_display = ("page", "created_at")
    list_filter = ("created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show pages owned by the current user
        return qs.filter(user=request.user).order_by("page_id").distinct("page_id")


modeladmin_register(NewsPageAdmin)
# modeladmin_register(MyPagesAdmin)
# modeladmin_register(MyPageRevisionsAdmin)
