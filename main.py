import os
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

from auth.get_token import get_access_token
from api.list.list_loda import fetch_laws
from api.consult.get_lawDecree import get_law_decree, extract_plain_text_from_law_decree
from api.consult.get_code import get_code, extract_plain_text_from_code
from api.consult.get_circulaire import get_circulaire, extract_plain_text_from_circulaire
from api.consult.get_article import get_article, extract_plain_text_from_article
from api.consult.get_tablematieres import get_table_matieres, extract_article_ids_from_toc
from api.consult.get_legi_part import get_legi_part
from api.consult.get_article_with_id_eli_or_alias import get_article_with_id_eli_or_alias  # AJOUT
from api.consult.get_article_by_cid import get_article_by_cid
from storage.save_text import save_law_text
from storage.save_json import save_law_as_json

from utils.logger import logger
from utils.rate_limiter import RateLimiter
from utils.extract_plain_text_from_generic import extract_plain_text_generic

load_dotenv()
rate_limiter = RateLimiter(max_requests_per_second=15)

# Constantes
today = datetime.now().date()
START_YEAR = 2023
END_YEAR = today.year

SAVE_TXT_FOLDER = os.getenv('SAVE_TXT_FOLDER', 'laws')
SAVE_JSON_FOLDER = os.getenv('SAVE_JSON_FOLDER', 'laws_json')


def clean_filename(title, max_length=150):
    invalid = '<>:/\\|?*"'
    for char in invalid:
        title = title.replace(char, '')
    cleaned = title.strip().replace(' ', '_')
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned


# AJOUT : fonction pour télécharger les articles liés
def download_articles_from_law(headers, articles, year_folder, month_folder, law_title):
    
    if not articles:
        return

    for article in articles:
        article_id = article.get('id')
        if article_id:
            try:
                logger.info(f"📜 Téléchargement de l'article {article_id} lié à '{law_title}'")
                article_data = get_article_by_cid(headers, article_id)  # ✅ ICI

                if article_data:
                    texte_html = article_data.get('article', {}).get('texteHtml', '')
                    if texte_html:
                        folder_path = os.path.join(SAVE_TXT_FOLDER, year_folder, month_folder, clean_filename(law_title))
                        os.makedirs(folder_path, exist_ok=True)

                        filepath = os.path.join(folder_path, f"{article_id}.txt")
                        save_law_text(filepath, article_id, texte_html)
                    else:
                        logger.warning(f"⚠️ Pas de texte trouvé pour l'article {article_id}")
                else:
                    logger.warning(f"⚠️ Pas de données reçues pour l'article {article_id}")

            except Exception as e:
                logger.error(f"❌ Erreur téléchargement article {article_id}: {str(e)}")
                time.sleep(2)

# Fonction principale pour télécharger un texte de loi
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

    headers = {"Authorization": f"Bearer {access_token}"}  # <=== headers créés ici ✅

    try:
        if nature == 'LODA':
            logger.info(f"📑 Téléchargement LOI/ORDO/DÉCRET (LODA) : {title}")
            response = get_law_decree(access_token, text_id)

        elif nature == 'CODE':
            logger.info(f"📑 Téléchargement CODE : {title}")
            response = get_code(access_token, text_id)

        elif nature == 'CIRCULAIRE':
            logger.info(f"📑 Téléchargement CIRCULAIRE : {title}")
            response = get_circulaire(access_token, text_id)

        else:
            logger.info(f"📑 Téléchargement brut (nature={nature}) pour {title}")
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

            # Correction ici: je passe headers à la fonction
            articles = response.get('articles', [])
            if articles:
                download_articles_from_law(headers, articles, year_folder, month_folder, title)

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
            time.sleep(0.1)  # Respect API

    logger.info("✨ Script terminé avec succès ✨")


if __name__ == "__main__":
    main()
