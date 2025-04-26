import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    """
    Récupère un access token OAuth2 depuis l'API PISTE
    """
    data = {
        'grant_type': 'client_credentials',
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'scope': 'openid'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    token_url = os.getenv('TOKEN_URL')

    response = requests.post(token_url, data=data, headers=headers)
    response.raise_for_status()

    access_token = response.json().get('access_token')
    return access_token
