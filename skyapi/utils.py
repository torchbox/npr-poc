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
        'type': 'Individual',
        "phone": {
            "number": details['phone']['number'],
            "type": details['phone']['type'],
            "do_not_call": details['phone']['consent'],
        },
        "address": {
            "address_lines": details['address']['address_lines'],
            "city": details['address']['city'],
            "country": details['address']['country'],
            "county": details['address']['county'],
            "postal_code": details['address']['postal_code'],
            "type": "Home",
        },
    }

    res = requests.post(
        'https://api.sky.blackbaud.com/constituent/v1/constituents',
        data=json.dumps(constituent_payload),
        headers=create_headers(access_token)
    )

    return res
