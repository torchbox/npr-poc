from django import template

from ..utils import render_snippet

register = template.Library()


@register.simple_tag
def story_summary(story):
    return render_snippet(story)
