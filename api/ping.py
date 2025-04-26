import os
import requests
from dotenv import load_dotenv

load_dotenv()

def ping_api(access_token):
    """
    Ping the Legifrance API to check access
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    ping_url = os.getenv('PING_URL')

    response = requests.get(ping_url, headers=headers)
    response.raise_for_status()
    return response.text
