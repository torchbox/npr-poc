import json
import requests
import datetime

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

    # Force a gift with the newly added constituent, IRL this would be a separate,
    # None required part of the form but for now we are just forcing a donation in
    # Campaign: "Individual Giving [16]"
    # Fund: "Acquisition Fund [4]"
    constituent_id = res.json()['id']

    gift_payload = {
        "amount": {
            "value": 100
        },
        "constituent_id": constituent_id,
        "date": datetime.datetime.now().isoformat(),

        "gift_splits": [
            {
            "amount": {
                "value": 100
            },
            "campaign_id": "16",
            "fund_id": "4"
            }
        ],
        "gift_status": "Active",
        "payments": [
            {
            "payment_method": "Cash"
            }
        ],
        "post_date": "2020-01-03T00:00:00",
        "post_status": "NotPosted",
        "reference": "newly added gift",
        "type": "Donation"
    }

    gift = requests.post(
        'https://api.sky.blackbaud.com/gift/v1/gifts',
        data=json.dumps(gift_payload),
        headers=create_headers(access_token)
    )

    return res

