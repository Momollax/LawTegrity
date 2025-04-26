
import requests
from dotenv import load_dotenv
from utils.logger import logger
from utils.rate_limiter import RateLimiter
import os
load_dotenv()
rateLimit = os.getenv('RATE_LIMIT')

rate_limiter = RateLimiter(max_requests_per_second=float(rateLimit))

def get_circulaire(access_token, circulaire_id):
    """
    Récupère une circulaire par son ID technique.
    """
    api_base_url = os.getenv('API_BASE_URL')
    url = api_base_url + '/consult/circulaire'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "id": circulaire_id
    }

    logger.info(f"Requête /consult/circulaire pour id: {circulaire_id}")
    rate_limiter.wait()
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()

def extract_plain_text_from_circulaire(content_json):
    """
    Extrait le texte brut d'une circulaire.
    """
    circulaire = content_json.get('circulaire', {})
    texte = circulaire.get('data') or circulaire.get('attachment', {}).get('content') or "Texte non disponible."
    return texte
