from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import AudioMedia


class AudioMediaAdmin(ModelAdmin):
    model = AudioMedia
    menu_label = 'Audio Media'
    menu_icon = 'media'
    menu_order = 200
    add_to_settings_menu = False
    list_display = ('title',)
    search_fields = ('title',)


modeladmin_register(AudioMediaAdmin)
