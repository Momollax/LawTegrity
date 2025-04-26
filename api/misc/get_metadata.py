import os
import requests
from dotenv import load_dotenv
from utils.logger import logger
from utils.rate_limiter import RateLimiter
from utils.decorators import auto_refresh_token

load_dotenv()
rateLimit = float(os.getenv('RATE_LIMIT', 5))
rate_limiter = RateLimiter(max_requests_per_second=rateLimit)

@auto_refresh_token
def get_metadata(access_token, text_id):
    """
    Récupère les métadonnées générales d'un texte par son textId.
    """
    api_base_url = os.getenv('API_BASE_URL')
    url = api_base_url + '/misc/getMetaData'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "textId": text_id
    }

    logger.info(f"Requête /misc/getMetaData pour textId: {text_id}")
    rate_limiter.wait()
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()
