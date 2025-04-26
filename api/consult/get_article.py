import os
import requests
from dotenv import load_dotenv
from utils.logger import logger
from utils.rate_limiter import RateLimiter
from dotenv import load_dotenv
load_dotenv()
rateLimit = os.getenv('RATE_LIMIT')

rate_limiter = RateLimiter(max_requests_per_second=float(rateLimit))

def get_article(access_token, article_id):
    """
    Récupère un article précis par son ID technique.
    """
    api_base_url = os.getenv('API_BASE_URL')
    url = api_base_url + '/consult/getArticle'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "id": article_id
    }

    logger.info(f"Requête /consult/getArticle pour id: {article_id}")
    rate_limiter.wait()
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()

def extract_plain_text_from_article(content_json):
    """
    Extrait le texte brut d'un article.
    """
    article = content_json.get('article', {})
    texte = article.get('texte') or article.get('texteHtml') or "Texte non disponible."
    return texte
