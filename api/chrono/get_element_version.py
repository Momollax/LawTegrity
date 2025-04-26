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
def get_element_versions(access_token, text_cid, element_cid):
    """
    Récupère l'historique d'un élément précis (section, article) d'un texte.
    """
    api_base_url = os.getenv('API_BASE_URL')
    url = api_base_url + '/chrono/textCidAndElementCid'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "textCid": text_cid,
        "elementCid": element_cid
    }

    logger.info(f"Requête /chrono/textCidAndElementCid pour textCid: {text_cid}, elementCid: {element_cid}")
    rate_limiter.wait()
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()
