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
def get_text_versions(access_token, text_cid, start_year, end_year):
    """
    Récupère toutes les versions d'un texte (code, loi, etc.) sur une période.
    """
    api_base_url = os.getenv('API_BASE_URL')
    url = api_base_url + '/chrono/textCid'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "textCid": text_cid,
        "startYear": start_year,
        "endYear": end_year
    }

    logger.info(f"Requête /chrono/textCid pour textCid: {text_cid}, de {start_year} à {end_year}")
    rate_limiter.wait()
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()
