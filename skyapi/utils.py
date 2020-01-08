import json
import requests

API_KEY = 'fc44377c4aa541f0955b16bb533154ff'


def create_headers(access_token):
    return {
        'Content-Type': 'application/json',
        'Bb-Api-Subscription-Key': API_KEY,
        'Authorization': f'Bearer {access_token}'
    }


def add_constituent(details, access_token):
    constituent_payload = {
        'email': {
            'address': details['email'],
            'type': 'Email'
        },
        'first': details['first_name'],
        'last': details['last_name'],
        'title': details['title'],
        'type': 'Individual'
    }

    res = requests.post(
        'https://api.sky.blackbaud.com/constituent/v1/constituents',
        data=json.dumps(constituent_payload),
        headers=create_headers(access_token)
    )

    return res
