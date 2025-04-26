import os
import requests
from dotenv import load_dotenv
from utils.logger import logger
from utils.rate_limiter import RateLimiter

load_dotenv()
rate_limiter = RateLimiter(max_requests_per_second=15)

def get_code(access_token, text_id, date_vigueur=None):
    """
    Récupère un Code juridique complet (ex : Code civil) depuis son textId.
    """
    api_base_url = os.getenv('API_BASE_URL')
    url = api_base_url + '/consult/code'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "textId": text_id
    }
    if date_vigueur:
        payload["date"] = date_vigueur

    logger.info(f"Requête /consult/code pour textId: {text_id}")
    rate_limiter.wait()
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()

def extract_plain_text_from_code(content_json):
    """
    Extrait tout le texte brut d'un Code (articles + sections).
    """
    textes = []

    # Articles directs
    articles = content_json.get('articles', [])
    for article in articles:
        titre = article.get('modificatorTitle') or article.get('num') or ""
        texte = article.get('content') or ""
        if texte:
            textes.append(f"{titre}\n{texte}")

    # Sections et leurs articles
    sections = content_json.get('sections', [])
    for section in sections:
        section_title = section.get('title', '')
        if section_title:
            textes.append(f"\n== {section_title} ==\n")
        section_articles = section.get('articles', [])
        for article in section_articles:
            titre = article.get('modificatorTitle') or article.get('num') or ""
            texte = article.get('content') or ""
            if texte:
                textes.append(f"{titre}\n{texte}")

    return "\n\n".join(textes) if textes else "Texte non disponible."
