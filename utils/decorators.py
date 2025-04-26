# utils/decorators.py

import time
import requests
from auth.get_token import get_access_token
from utils.logger import logger
from utils.rate_limiter import RateLimiter
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
rateLimit = os.getenv('RATE_LIMIT', 5)
rate_limiter = RateLimiter(max_requests_per_second=float(rateLimit))

def auto_refresh_token(func):
    """
    Décorateur pour rafraîchir automatiquement le token si 401 Unauthorized.
    """

    def wrapper(*args, **kwargs):
        access_token = kwargs.get('access_token')
        max_attempts = 5

        for attempt in range(max_attempts):
            rate_limiter.wait()

            try:
                response = func(*args, **kwargs)

                if hasattr(response, 'status_code'):
                    if response.status_code == 401:
                        logger.warning(f"🔄 Token expiré. Renouvellement en cours... (tentative {attempt+1}/{max_attempts})")
                        access_token = get_access_token()
                        kwargs['access_token'] = access_token
                        continue

                    if response.status_code == 429:
                        logger.warning(f"⚠️ 429 Too Many Requests. Pause 10s... (tentative {attempt+1}/{max_attempts})")
                        time.sleep(10)
                        continue

                    response.raise_for_status()

                return response  # Retourne la réponse directe (ex: .json() ou response)

            except requests.RequestException as e:
                logger.error(f"❌ Exception API : {e}")
                time.sleep(5)

        logger.error(f"⛔ Echec après {max_attempts} tentatives pour {func.__name__}")
        return None

    return wrapper
