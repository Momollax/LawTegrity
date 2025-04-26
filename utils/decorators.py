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
    def wrapper(access_token, *args, **kwargs):
        max_retries = 2  # Une fois re-tenté après renouvellement

        for attempt in range(max_retries):
            try:
                result = func(access_token, *args, **kwargs)
                return result
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    logger.warning(f"🔄 Token expiré. Renouvellement en cours... (tentative {attempt + 1})")
                    
                    # Re-demander un nouveau token
                    new_token = get_access_token()
                    access_token = new_token
                    
                    # PING test
                    if not test_token(new_token):
                        logger.error("❌ Nouveau token invalide après rafraîchissement.")
                        raise Exception("Erreur lors du renouvellement du token.")

                    # Sinon, réessayer une dernière fois avec nouveau token
                else:
                    raise  # autre erreur HTTP
        raise Exception("🔴 Token refresh failed après plusieurs tentatives.")
    return wrapper

def test_token(access_token):
    """
    Vérifie si le token est valide avec un ping Legifrance.
    """
    url = os.getenv('API_BASE_URL') + '/consult/ping'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Erreur lors du test ping: {e}")
        return False