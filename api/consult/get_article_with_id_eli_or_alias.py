import requests

def get_article_with_id_eli_or_alias(headers, article_id):
    """
    Récupère le contenu d'un article à partir de son identifiant ELI ou alias.

    Args:
        headers (dict): Headers HTTP avec le token d'authentification.
        article_id (str): L'identifiant ELI ou alias de l'article (ex: "LEGIARTI000046891924").

    Returns:
        dict: Données JSON de l'article récupéré.
    """
    url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticleWithIdEliOrAlias"
    payload = {
        "idEliOrAlias": article_id
    }

    response = requests.post(url, headers=headers, json=payload)
    print("headers:", headers, "json:", payload, "response:", response.text)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erreur lors de la récupération de l'article {article_id} : {response.status_code} - {response.text}")
