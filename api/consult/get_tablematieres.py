# === Nouveau get_table_matieres.py corrigé ===
import requests
from utils.logger import logger
import time
from utils.rate_limiter import RateLimiter
import os
from dotenv import load_dotenv
load_dotenv()
rateLimit = os.getenv('RATE_LIMIT')

rate_limiter = RateLimiter(max_requests_per_second=float(rateLimit))

def get_table_matieres(access_token, text_id, date, nature="LODA"):
    url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legi/tableMatieres"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    if date and "T" in date:
        date = date.split("T")[0]
    data = {
        "textId": text_id,
        "date": date,
        "nature": nature
    }

    max_retries = 3
    retry_delay = 10  # secondes d'attente en cas de 429
    inter_request_delay = 1  # délai après CHAQUE requête pour ne pas spammer l'API

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            print("response de consult/legi/tableMatieres:",headers, data, response.text)
            rate_limiter.wait() 
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                logger.error(f"⚠️ Mauvaise requête (400) pour textId={text_id}. Vérifie les paramètres envoyés.")
                return None
            elif response.status_code == 404:
                logger.error(f"⚠️ Sommaire non trouvé (404) pour textId={text_id}.")
                return None
            elif response.status_code == 429:
                logger.warning(f"⚠️ 429 Too Many Requests pour textId={text_id}... Attente {retry_delay} secondes avant retry (tentative {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                logger.error(f"⚠️ Erreur {response.status_code} inconnue pour textId={text_id}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Exception pendant la requête get_table_matieres pour textId={text_id} : {str(e)}")
            time.sleep(retry_delay)

    logger.error(f"❌ Échec après {max_retries} tentatives pour obtenir le sommaire de textId={text_id}")
    return None

def extract_article_ids_from_toc(toc_response):
    if not toc_response or not isinstance(toc_response, dict):
        return []

    article_ids = []

    # Extraction directe si des articles existent
    if "articles" in toc_response:
        for article in toc_response["articles"]:
            if "id" in article:
                article_ids.append(article["id"])

    # Extraction récursive des sections
    def explore_sections(sections):
        for section in sections:
            if "articles" in section:
                for article in section["articles"]:
                    if "id" in article:
                        article_ids.append(article["id"])
            if "sections" in section:
                explore_sections(section["sections"])

    sections = toc_response.get("sections", [])
    explore_sections(sections)

    return article_ids
