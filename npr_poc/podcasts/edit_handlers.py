from wagtailmedia.widgets import AdminMediaChooser
from wagtailmedia.edit_handlers import BaseMediaChooserPanel


class MediaChooserPanel(BaseMediaChooserPanel):

    # def __init__(self, field_name):
    #     self.field_name = field_name
    #     self.heading = 'something'

    def widget_overrides(self):
        return {self.field_name: AdminMediaChooser}
