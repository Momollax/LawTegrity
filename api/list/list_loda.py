import os
import requests
from dotenv import load_dotenv
from utils.split_dates import split_months, split_days
from utils.logger import logger
from utils.rate_limiter import RateLimiter
from time import sleep

load_dotenv()

PAGE_SIZE = int(os.getenv('PAGE_SIZE', 100))
THRESHOLD = int(os.getenv('THRESHOLD_LIMIT', 1000))
rateLimit = os.getenv('RATE_LIMIT')  # Limite par défaut de 5 requêtes par seconde

rate_limiter = RateLimiter(max_requests_per_second=float(rateLimit))

def post_loda(access_token, start_date, end_date, page):
    """
    Effectue une requête POST vers /list/loda pour une période donnée.
    """
    api_base_url = os.getenv('API_BASE_URL')
    url = api_base_url + '/list/loda'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "sort": "PUBLICATION_DATE_ASC",
        "legalStatus": ["VIGUEUR", "ABROGE", "VIGUEUR_DIFF"],
        "natures": ["LOI", "ORDONNANCE", "DECRET"],
        "pageNumber": page,
        "pageSize": PAGE_SIZE,
        "signatureDate": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "publicationDate": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "secondSort": "PUBLICATION_DATE_ASC"
    }

    for attempt in range(3):  # 3 tentatives max
        try:
            rate_limiter.wait()
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.warning(f"⚠️ 429 Too Many Requests - attente 5 secondes (tentative {attempt + 1})")
                sleep(5)
            elif response.status_code >= 500:
                logger.warning(f"⚠️ Erreur serveur {response.status_code} - attente 5 secondes (tentative {attempt + 1})")
                sleep(5)
            else:
                logger.error(f"❌ Erreur critique : {e}")
                raise e
    logger.error("❌ Échec après 3 tentatives, abandon de cette période")
    raise Exception("Erreur persistante sur POST /list/loda")

def fetch_laws(access_token, start_date, end_date):
    """
    Récupère toutes les lois entre deux dates, 
    découpe automatiquement si la période est trop chargée.
    """
    logger.info(f"Analyse de la période {start_date} -> {end_date}")

    try:
        first_page = post_loda(access_token, start_date, end_date, page=1)
    except Exception as e:
        logger.error(f"Erreur fatale sur la période {start_date} -> {end_date}: {e}")
        return  # abandonne cette période

    total_results = first_page.get('totalResultNumber', 0)
    logger.info(f"Total de résultats trouvés: {total_results}")

    if total_results > THRESHOLD:
        logger.warning(f"⚠️ Trop de résultats ({total_results}) pour {start_date} -> {end_date}, découpage nécessaire")

        days_span = (end_date - start_date).days

        if days_span > 31:
            logger.info("Découpage par mois")
            for start, end in split_months(start_date.year):
                if start >= start_date and end <= end_date:
                    yield from fetch_laws(access_token, start, end)
        else:
            logger.info("Découpage par jour")
            for start, end in split_days(start_date.year, start_date.month):
                if start >= start_date and end <= end_date:
                    yield from fetch_laws(access_token, start, end)
    else:
        logger.info(f"Récupération directe ({total_results} résultats)")

        current_page = 1
        while True:
            logger.info(f"Fetching page {current_page} pour {start_date.year}")
            try:
                data = post_loda(access_token, start_date, end_date, page=current_page)
            except Exception as e:
                logger.error(f"Erreur lors du fetch de la page {current_page} : {e}")
                break

            results = data.get('results', [])
            if not results:
                logger.info(f"Fin des résultats pour {start_date.year} page {current_page}")
                break

            for law in results:
                yield law

            current_page += 1
