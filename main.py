import os
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

from auth.get_token import get_access_token
from api.list.list_loda import fetch_laws
from api.consult.get_lawDecree import get_law_decree
from api.consult.get_code import get_code
from api.consult.get_circulaire import get_circulaire
from api.consult.get_article import get_article
from api.consult.get_tablematieres import get_table_matieres
from api.consult.get_legi_part import get_legi_part
from api.consult.get_article_with_id_eli_or_alias import get_article_with_id_eli_or_alias

from storage.save_text import save_law_text
from storage.save_json import save_law_as_json

from utils.logger import logger
from utils.rate_limiter import RateLimiter
from utils.extract_plain_text_from_generic import extract_plain_text_generic
from api.consult.get_article_by_cid import get_article_by_cid
load_dotenv()

rateLimit = os.getenv('RATE_LIMIT')
start_date = os.getenv('START_DATE')
rate_limiter = RateLimiter(max_requests_per_second=float(rateLimit))

# Constantes
today = datetime.now().date()
START_YEAR = int(start_date)
END_YEAR = today.year
SAVE_TXT_FOLDER = os.getenv('SAVE_TXT_FOLDER', 'laws')
SAVE_JSON_FOLDER = os.getenv('SAVE_JSON_FOLDER', 'laws_json')

def clean_filename(title, max_length=80):
    invalid = '<>:/\\|?*"'
    for char in invalid:
        title = title.replace(char, '')
    title = title.replace(' ', '_')
    cleaned = title.strip()

    # Retirer aussi les apostrophes et caractères spéciaux qui posent problème
    cleaned = cleaned.replace("’", "").replace("'", "")

    # Raccourcir si trop long
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned

# Correction: on passe access_token dans la fonction
def download_articles_from_law(articles, year_folder, month_folder, law_title):
    if not articles:
        return

    # Créer un sous-dossier par loi
    folder_path = os.path.join(SAVE_TXT_FOLDER, year_folder, month_folder, clean_filename(law_title))
    os.makedirs(folder_path, exist_ok=True)

    for article in articles:
        article_id = article.get('id')
        texte_html = article.get('content', '')

        if article_id and texte_html:
            try:
                logger.info(f"📜 Sauvegarde de l'article {article_id} lié à '{law_title}'")
                save_law_text(folder_path, article_id, texte_html)

            except Exception as e:
                logger.error(f"❌ Erreur en sauvegardant l'article {article_id}: {str(e)}")
                time.sleep(2)
        else:
            logger.warning(f"⚠️ Article {article_id} sans contenu détecté")

def download_law(access_token, law_data):
    nature = law_data.get('nature', '').upper()
    title = law_data.get('titre', law_data.get('title', 'Sans titre'))
    text_id = law_data.get('id', law_data.get('textId', ''))
    publication_date = law_data.get('dateDebut', law_data.get('date', ''))

    if not text_id:
        logger.warning(f"Pas d'ID trouvé pour {title}, skipping.")
        return

    year_folder = publication_date[:4] if publication_date else str(today.year)
    month_folder = publication_date[5:7] if publication_date else '01'

    save_path_txt = os.path.join(SAVE_TXT_FOLDER, year_folder, month_folder)
    save_path_json = os.path.join(SAVE_JSON_FOLDER, year_folder, month_folder)

    os.makedirs(save_path_txt, exist_ok=True)
    os.makedirs(save_path_json, exist_ok=True)

    filename = clean_filename(f"{nature}_{title}")

    try:
        if nature == 'LODA':
            logger.info(f"\U0001F4D1 Téléchargement LOI/ORDO/DÉCRET (LODA) : {title}")
            response = get_law_decree(access_token, text_id)

        elif nature == 'CODE':
            logger.info(f"\U0001F4D1 Téléchargement CODE : {title}")
            response = get_code(access_token, text_id)

        elif nature == 'CIRCULAIRE':
            logger.info(f"\U0001F4D1 Téléchargement CIRCULAIRE : {title}")
            response = get_circulaire(access_token, text_id)

        else:
            logger.info(f"\U0001F4D1 Téléchargement brut (nature={nature}) pour {title}")
            response = get_legi_part(access_token, text_id, publication_date)
            if response:
                text = extract_plain_text_generic(response)
                save_law_text(save_path_txt, filename, text)
                save_law_as_json(save_path_json, filename, response)
            else:
                logger.error(f"Impossible de récupérer {title} même avec legi_part.")

        if response:
            text = extract_plain_text_generic(response)
            save_law_text(save_path_txt, filename, text)
            save_law_as_json(save_path_json, filename, response)

            articles = response.get('articles', [])
            if articles:
                download_articles_from_law(articles, year_folder, month_folder, title)

        else:
            logger.warning(f"Pas de réponse pour {title} ({text_id})")

    except Exception as e:
        logger.error(f"❌ Erreur téléchargement {title} ({text_id}): {str(e)}")
        with open('logs/failed_downloads.txt', 'a', encoding='utf-8') as f:
            f.write(f"FAILED: {text_id} {title}\n")
        time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description="Télécharger tous les textes de lois français depuis Legifrance API.")
    parser.add_argument('--start-year', type=int, default=START_YEAR, help='Année de début')
    parser.add_argument('--end-year', type=int, default=END_YEAR, help='Année de fin')
    args = parser.parse_args()

    logger.info("Démarrage du script Legifrance Integrity 🚀")

    access_token = get_access_token()
    logger.info("Token OAuth récupéré avec succès ✅")

    for year in range(args.start_year, args.end_year + 1):
        logger.info(f"=== Récupération des lois pour {year} ===")

        laws = fetch_laws(access_token, datetime(year, 1, 1).date(), datetime(year, 12, 31).date())

        for law in laws:
            download_law(access_token, law)
            time.sleep(0.1)

    logger.info("✨ Script terminé avec succès ✨")

if __name__ == "__main__":
    main()
