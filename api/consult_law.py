import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_law_content(access_token, text_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = os.getenv('API_BASE_URL') + '/consult/legiPart'

    payload = {"textId": text_id}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
