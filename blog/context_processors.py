"""
Context processors pour le Blog Académique.

Ce module fournit des variables de contexte globales
disponibles dans tous les templates.
"""

import logging
from blog.db_operations import (
    obtenir_toutes_configurations,
    obtenir_statistiques_globales,
)

logger = logging.getLogger(__name__)


def contexte_global(request):
    """
    Ajoute des variables globales au contexte de tous les templates.

    Retourne:
        dict: Variables de contexte globales incluant la configuration du site
    """
    try:
        config = obtenir_toutes_configurations()
        stats = obtenir_statistiques_globales()

        # Transformer en objet accessible par attribut
        config_site = {
            "nom_site": config.get("nom_site", "Blog Académique"),
            "description_site": config.get(
                "description_site",
                "Blog académique - Articles, recherches et publications",
            ),
            "email_contact": config.get("email_contact", ""),
            "telephone": config.get("telephone", ""),
            "adresse": config.get("adresse", ""),
            "lien_facebook": config.get("lien_facebook", ""),
            "lien_twitter": config.get("lien_twitter", ""),
            "lien_linkedin": config.get("lien_linkedin", ""),
            "lien_youtube": config.get("lien_youtube", ""),
            "lien_instagram": config.get("lien_instagram", ""),
            "mots_cles": config.get(
                "mots_cles", "professeur, université, recherche, publications, livres"
            ),
            "copyright_texte": config.get("copyright_texte", ""),
            "google_analytics_id": config.get("google_analytics_id", ""),
        }

    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {e}")
        # Valeurs par défaut en cas d'erreur
        config_site = {
            "nom_site": "Blog Académique",
            "description_site": "Blog académique - Articles, recherches et publications",
            "email_contact": "",
            "telephone": "",
            "adresse": "",
            "lien_facebook": "",
            "lien_twitter": "",
            "lien_linkedin": "",
            "lien_youtube": "",
            "lien_instagram": "",
            "mots_cles": "professeur, université, recherche, publications, livres",
            "copyright_texte": "",
            "google_analytics_id": "",
        }
        stats = {}

    return {
        "config_site": config_site,
        "stats": stats,
    }
