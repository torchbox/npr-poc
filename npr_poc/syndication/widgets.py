from generic_chooser.widgets import AdminChooser

from .utils import get_story


class SyndicatedContentChooser(AdminChooser):
    choose_one_text = 'Choose news item'
    choose_another_text = 'Choose another news item'
    choose_modal_url_name = 'npr_syndication_choose_content'

    def get_instance(self, value):
        return get_story(value)

    def get_title(self, instance):
        return instance['title']
