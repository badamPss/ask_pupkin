import requests
from django.conf import settings

def publish_to_centrifugo(channel, data):
    try:
        url = settings.CENTRIFUGO_API_URL
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': settings.CENTRIFUGO_API_KEY
        }
        payload = {
            'method': 'publish',
            'params': {
                'channel': channel,
                'data': data
            }
        }
        response = requests.post(url, json=payload, headers=headers, timeout=2)
        response.raise_for_status()
        return True
    except Exception:
        return False
