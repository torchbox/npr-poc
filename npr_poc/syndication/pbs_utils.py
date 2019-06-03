from functools import lru_cache
from dateutil.parser import parse

from django.conf import settings


import requests
from requests.auth import HTTPBasicAuth


STAGING_ENDPOINT = "https://media-staging.services.pbs.org/api/v1"


def show_to_dict(show):
    return {
        "id": show["id"],
        "title": show["attributes"]["title"],
        "updated_at": parse(show["attributes"]["updated_at"]).date(),
    }


@lru_cache(maxsize=500)
def search_shows(search_term):
    if not search_term:
        return []
    response = requests.get(
        STAGING_ENDPOINT + "/shows/search/?query=" + search_term,
        auth=HTTPBasicAuth(settings.PBS_API_KEY, settings.PBS_API_SECRET),
    )
    if response.status_code == 200:
        return response.json()["data"]
    return []


@lru_cache(maxsize=500)
def show_details(show_id):
    response = requests.get(
        f"{STAGING_ENDPOINT}/shows/{show_id}/",
        auth=HTTPBasicAuth(settings.PBS_API_KEY, settings.PBS_API_SECRET),
    )
    if response.status_code == 200:
        return response.json()["data"]["attributes"]
    return []

