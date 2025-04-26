import os
import requests
from dotenv import load_dotenv
from utils.logger import logger
from utils.rate_limiter import RateLimiter

load_dotenv()
rate_limiter = RateLimiter(max_requests_per_second=15)

def get_article_by_cid(access_token, cid):
    """
    Récupère toutes les versions d'un article à partir de son cid.
    """
    api_base_url = os.getenv('API_BASE_URL')
    url = api_base_url + '/consult/getArticleByCid'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "cid": cid
    }
    print(f"cid: {cid}")
    logger.info(f"Requête /consult/getArticleByCid pour cid: {cid}")
    rate_limiter.wait()
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()

def extract_plain_text_from_articles(content_json):
    """
    Extrait tout le texte brut depuis les différentes versions d'un article.
    """
    textes = []
    articles = content_json.get('listArticle', [])
    if not articles:
        return "Texte non disponible."
    for article in articles:
        version_info = article.get('versionArticle', '')
        numero = article.get('num', '')
        texte = article.get('texte') or article.get('texteHtml') or ""

        header = f"Version {version_info} - Article {numero}"
        textes.append(f"{header}\n{texte}")

    return "\n\n".join(textes) if textes else "Texte non disponible."
