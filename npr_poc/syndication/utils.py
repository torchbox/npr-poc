from functools import lru_cache

from django.conf import settings
from django.template.loader import render_to_string

from bs4 import BeautifulSoup
from dateutil.parser import parse
import requests


API_URL = 'http://api.npr.org/query'


def story_to_dict(story):
    from .models import SyndicatedNewsPage      # Avoid circular import

    try:
        image = story.find('image', {'type': 'primary'})['src']
    except (AttributeError, TypeError):
        image = None

    return {
        'id': story['id'],
        'title': story.title.text,
        'url': story.find('link', {'type': 'html'}).text,
        'org': story.organization.find('name', ).text,
        'date': parse(story.storyDate.text).date(),
        'teaser': story.teaser.text,
        'image': image,
        'html': story.fullText.text,
        'syndicated_page': SyndicatedNewsPage.objects.filter(story=story['id']).first(),
    }


@lru_cache(maxsize=500)
def get_story(id):
    response = requests.get(API_URL, params={'apiKey': settings.NPR_API_KEY, 'id': id})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')
        story = soup.list.story
        return story_to_dict(story)


@lru_cache(maxsize=500)
def search_stories(search_term, org=None):
    params = {'apiKey': settings.NPR_API_KEY}
    if search_term:
        params['searchTerm'] = search_term
        params['sort'] = 'relevance'
    else:
        params['sort'] = 'date'

    if org:
        params['orgId'] = org

    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')
        stories = soup.list.find_all('story')
        return stories

    return []


def render_snippet(story):
    return render_to_string('generic_chooser/widgets/npr_chooser_string.html', story)
