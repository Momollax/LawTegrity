# api/consult/get_legi_part.py

import requests
import time
from utils.logger import logger
from utils.rate_limiter import RateLimiter
from auth.get_token import get_access_token
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

rateLimit = os.getenv('RATE_LIMIT', 5)  # Défaut 5 requêtes/sec si non défini
rate_limiter = RateLimiter(max_requests_per_second=float(rateLimit))
from utils.decorators import auto_refresh_token
@auto_refresh_token
def get_legi_part(access_token, text_id, date=None):
    """
    Récupère le contenu d'un texte du fonds LEGI par son textId.
    Si la requête échoue avec 401 Unauthorized, le token est automatiquement renouvelé.
    """
    url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "textId": text_id
    }
    if date:
        payload["date"] = date

    for attempt in range(5):  # 5 tentatives max
        try:
            rate_limiter.wait()
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 401:
                logger.warning(f"🔄 Token expiré. Renouvellement en cours... (tentative {attempt+1})")
                access_token = get_token()
                headers["Authorization"] = f"Bearer {access_token}"
                continue

            if response.status_code == 429:
                logger.warning(f"⚠️ 429 Too Many Requests. Pause 10s... (tentative {attempt+1})")
                time.sleep(10)
                continue

            if response.status_code == 400:
                logger.error(f"❌ 400 Bad Request pour textId={text_id}. Payload envoyé: {payload}")
                return None

            response.raise_for_status()

            logger.debug(f"✅ Réponse reçue pour textId={text_id}")
            return response.json()

        except requests.RequestException as e:
            logger.error(f"❌ Exception dans get_legi_part pour textId={text_id}: {e}")
            time.sleep(5)

    logger.error(f"⛔ Echec total après 5 tentatives pour textId={text_id}")
    return None
