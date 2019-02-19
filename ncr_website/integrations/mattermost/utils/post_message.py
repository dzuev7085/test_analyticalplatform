"""This module posts a message to Mattermost."""
import json

import requests


def post_message(webhook, channel, text):
    payload = {
        "channel": channel,
        'text': text,
    }
    headers = {'content-type': 'application/json',
               'Accept-Charset': 'UTF-8'}

    requests.post(
        webhook,
        data=json.dumps(payload),
        headers=headers,
    )
