import requests
import time
from utils.logger import logger
from utils.rate_limiter import RateLimiter
import os
from dotenv import load_dotenv
load_dotenv()
rateLimit = os.getenv('RATE_LIMIT')

rate_limiter = RateLimiter(max_requests_per_second=float(rateLimit))

def get_legi_part(access_token, text_id, date=None):
    url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "textId": text_id
    }
    if date:
        payload["date"] = date  # ajouter la date si fournie

    for attempt in range(3):  # 3 tentatives max
        try:
            response = requests.post(url, headers=headers, json=payload)
            rate_limiter.wait()
            if response.status_code == 429:
                logger.warning(f"⚠️ 429 Too Many Requests dans get_legi_part... Sleep 10s (tentative {attempt+1}/3)")
                time.sleep(10)
                continue
            response.raise_for_status()
            logger.debug(f"✅ Réponse reçue pour textId={text_id}")
            time.sleep(1)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"❌ Erreur dans get_legi_part pour textId={text_id}: {e}")
            time.sleep(5)

    return None
