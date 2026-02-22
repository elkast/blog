"""
Opérations de base de données pour le Blog Académique du Professeur.

Ce module contient toutes les fonctions d'accès à la base de données
utilisant des requêtes SQL brutes avec SQLite3.

IMPORTANT: Ce projet n'utilise PAS l'ORM Django.
Toutes les opérations sont effectuées en SQL brut.
"""

import sqlite3
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# UTILITAIRES DE CONNEXION
# =============================================================================


def obtenir_connexion():
    """Obtient une connexion à la base de données."""
    return sqlite3.connect(settings.DATABASES["default"]["NAME"])


def executer_requete(
    requete, parametres=None, fetchone=False, fetchall=False, commit=False
):
    """Exécute une requête SQL de manière sécurisée."""
    connexion = obtenir_connexion()
    curseur = connexion.cursor()

    try:
        if parametres:
            curseur.execute(requete, parametres)
        else:
            curseur.execute(requete)

        if commit:
            connexion.commit()

        if fetchone:
            return curseur.fetchone()
        elif fetchall:
            return curseur.fetchall()
        else:
            return curseur.lastrowid

    except Exception as e:
        logger.error(f"Erreur SQL: {e}")
        connexion.rollback()
        raise
    finally:
        connexion.close()


# =============================================================================
# OPÉRATIONS SUR LES ARTICLES
# =============================================================================


def obtenir_tous_articles(
    limite=None, type_article=None, est_vedette=None, est_publie=None
):
    """Récupère tous les articles avec filtres optionnels."""
    requete = """
        SELECT a.*, GROUP_CONCAT(c.nom) as categories_noms
        FROM articles a
        LEFT JOIN article_categories ac ON a.id = ac.article_id
        LEFT JOIN categories c ON ac.categorie_id = c.id
        WHERE 1=1
    """
    parametres = []

    if type_article:
        requete += " AND a.type_article = ?"
        parametres.append(type_article)

    if est_vedette is not None:
        requete += " AND a.est_vedette = ?"
        parametres.append(est_vedette)

    if est_publie is not None:
        requete += " AND a.est_publie = ?"
        parametres.append(est_publie)

    requete += " GROUP BY a.id ORDER BY a.ordre_affichage ASC, a.date_creation DESC"

    if limite:
        requete += " LIMIT ?"
        parametres.append(limite)

    resultats = executer_requete(requete, parametres, fetchall=True)

    articles = []
    for row in resultats:
        article = {
            "id": row[0],
            "titre": row[1],
            "slug": row[2],
            "contenu": row[3],
            "extrait": row[4],
            "type_article": row[5],
            "image_url": row[6],
            "banniere_url": row[7],
            "auteur": row[8],
            "temps_lecture": row[9],
            "est_vedette": row[10],
            "est_populaire": row[11],
            "est_nouveau": row[12],
            "est_publie": row[13],
            "ordre_affichage": row[14],
            "meta_keywords": row[15],
            "meta_description": row[16],
            "date_publication": row[17],
            "date_creation": row[18],
            "date_modification": row[19],
            "categories_noms": row[20] or "",
        }
        articles.append(article)

    return articles


def obtenir_article_par_id(article_id):
    """Recupere un article par son ID."""
    requete = """
        SELECT a.*, GROUP_CONCAT(c.nom) as categories_noms, GROUP_CONCAT(c.id) as categories_ids
        FROM articles a
        LEFT JOIN article_categories ac ON a.id = ac.article_id
        LEFT JOIN categories c ON ac.categorie_id = c.id
        WHERE a.id = ?
        GROUP BY a.id
    """
    row = executer_requete(requete, (article_id,), fetchone=True)

    if not row:
        return None

    return {
        "id": row[0],
        "titre": row[1],
        "slug": row[2],
        "contenu": row[3],
        "extrait": row[4],
        "type_article": row[5],
        "image_url": row[6],
        "banniere_url": row[7],
        "auteur": row[8],
        "temps_lecture": row[9],
        "est_vedette": row[10],
        "est_populaire": row[11],
        "est_nouveau": row[12],
        "est_publie": row[13],
        "ordre_affichage": row[14],
        "meta_keywords": row[15],
        "meta_description": row[16],
        "date_publication": row[17],
        "date_creation": row[18],
        "date_modification": row[19],
        "categories_noms": row[20] or "",
        "categories_ids": row[21] or "",
    }


def obtenir_article_par_slug(slug):
    """Recupere un article par son slug."""
    requete = """
        SELECT a.*, GROUP_CONCAT(c.nom) as categories_noms, GROUP_CONCAT(c.id) as categories_ids
        FROM articles a
        LEFT JOIN article_categories ac ON a.id = ac.article_id
        LEFT JOIN categories c ON ac.categorie_id = c.id
        WHERE a.slug = ? AND a.est_publie = 1
        GROUP BY a.id
    """
    row = executer_requete(requete, (slug,), fetchone=True)

    if not row:
        return None

    return {
        "id": row[0],
        "titre": row[1],
        "slug": row[2],
        "contenu": row[3],
        "extrait": row[4],
        "type_article": row[5],
        "image_url": row[6],
        "banniere_url": row[7],
        "auteur": row[8],
        "temps_lecture": row[9],
        "est_vedette": row[10],
        "est_populaire": row[11],
        "est_nouveau": row[12],
        "est_publie": row[13],
        "ordre_affichage": row[14],
        "meta_keywords": row[15],
        "meta_description": row[16],
        "date_publication": row[17],
        "date_creation": row[18],
        "date_modification": row[19],
        "categories_noms": row[20] or "",
        "categories_ids": row[21] or "",
    }


def obtenir_articles_vedettes(limite=6):
    """Recupere les articles vedettes."""
    return obtenir_tous_articles(limite=limite, est_vedette=1, est_publie=1)


def obtenir_articles_populaires(limite=6):
    """Recupere les articles populaires."""
    return obtenir_tous_articles(limite=limite, est_publie=1)


def obtenir_articles_plus_lus(limite=6):
    """Recupere les articles les plus lus."""
    requete = """
        SELECT a.*, GROUP_CONCAT(c.nom) as categories_noms,
               COALESCE(SUM(sv.nombre_vues), 0) as total_vues
        FROM articles a
        LEFT JOIN article_categories ac ON a.id = ac.article_id
        LEFT JOIN categories c ON ac.categorie_id = c.id
        LEFT JOIN statistiques_vues sv ON a.id = sv.article_id
        WHERE a.est_publie = 1
        GROUP BY a.id
        ORDER BY total_vues DESC, a.date_creation DESC
        LIMIT ?
    """
    resultats = executer_requete(requete, (limite,), fetchall=True)

    articles = []
    for row in resultats:
        article = {
            "id": row[0],
            "titre": row[1],
            "slug": row[2],
            "contenu": row[3],
            "extrait": row[4],
            "type_article": row[5],
            "image_url": row[6],
            "banniere_url": row[7],
            "auteur": row[8],
            "temps_lecture": row[9],
            "est_vedette": row[10],
            "est_populaire": row[11],
            "est_nouveau": row[12],
            "est_publie": row[13],
            "ordre_affichage": row[14],
            "meta_keywords": row[15],
            "meta_description": row[16],
            "date_publication": row[17],
            "date_creation": row[18],
            "date_modification": row[19],
            "categories_noms": row[20] or "",
        }
        articles.append(article)

    return articles


def obtenir_derniers_articles(limite=6):
    """Recupere les derniers articles publies."""
    requete = """
        SELECT a.*, GROUP_CONCAT(c.nom) as categories_noms
        FROM articles a
        LEFT JOIN article_categories ac ON a.id = ac.article_id
        LEFT JOIN categories c ON ac.categorie_id = c.id
        WHERE a.est_publie = 1
        GROUP BY a.id
        ORDER BY a.date_creation DESC
        LIMIT ?
    """
    resultats = executer_requete(requete, (limite,), fetchall=True)

    articles = []
    for row in resultats:
        article = {
            "id": row[0],
            "titre": row[1],
            "slug": row[2],
            "contenu": row[3],
            "extrait": row[4],
            "type_article": row[5],
            "image_url": row[6],
            "banniere_url": row[7],
            "auteur": row[8],
            "temps_lecture": row[9],
            "est_vedette": row[10],
            "est_populaire": row[11],
            "est_nouveau": row[12],
            "est_publie": row[13],
            "ordre_affichage": row[14],
            "meta_keywords": row[15],
            "meta_description": row[16],
            "date_publication": row[17],
            "date_creation": row[18],
            "date_modification": row[19],
            "categories_noms": row[20] or "",
        }
        articles.append(article)

    return articles


def rechercher_articles(terme, limite=20):
    """Recherche des articles par terme."""
    requete = """
        SELECT a.*, GROUP_CONCAT(c.nom) as categories_noms
        FROM articles a
        LEFT JOIN article_categories ac ON a.id = ac.article_id
        LEFT JOIN categories c ON ac.categorie_id = c.id
        WHERE a.est_publie = 1
          AND (a.titre LIKE ? OR a.contenu LIKE ? OR a.extrait LIKE ?)
        GROUP BY a.id
        ORDER BY a.date_creation DESC
        LIMIT ?
    """
    pattern = f"%{terme}%"
    resultats = executer_requete(
        requete, (pattern, pattern, pattern, limite), fetchall=True
    )

    articles = []
    for row in resultats:
        article = {
            "id": row[0],
            "titre": row[1],
            "slug": row[2],
            "contenu": row[3],
            "extrait": row[4],
            "type_article": row[5],
            "image_url": row[6],
            "banniere_url": row[7],
            "auteur": row[8],
            "temps_lecture": row[9],
            "est_vedette": row[10],
            "est_populaire": row[11],
            "est_nouveau": row[12],
            "est_publie": row[13],
            "ordre_affichage": row[14],
            "meta_keywords": row[15],
            "meta_description": row[16],
            "date_publication": row[17],
            "date_creation": row[18],
            "date_modification": row[19],
            "categories_noms": row[20] or "",
        }
        articles.append(article)

    return articles


def obtenir_articles_par_categorie(slug_categorie, limite=50):
    """Recupere les articles d'une categorie."""
    requete = """
        SELECT a.*, GROUP_CONCAT(c.nom) as categories_noms
        FROM articles a
        JOIN article_categories ac ON a.id = ac.article_id
        JOIN categories c ON ac.categorie_id = c.id
        WHERE c.slug = ? AND a.est_publie = 1
        GROUP BY a.id
        ORDER BY a.ordre_affichage ASC, a.date_creation DESC
        LIMIT ?
    """
    resultats = executer_requete(requete, (slug_categorie, limite), fetchall=True)

    articles = []
    for row in resultats:
        article = {
            "id": row[0],
            "titre": row[1],
            "slug": row[2],
            "contenu": row[3],
            "extrait": row[4],
            "type_article": row[5],
            "image_url": row[6],
            "banniere_url": row[7],
            "auteur": row[8],
            "temps_lecture": row[9],
            "est_vedette": row[10],
            "est_populaire": row[11],
            "est_nouveau": row[12],
            "est_publie": row[13],
            "ordre_affichage": row[14],
            "meta_keywords": row[15],
            "meta_description": row[16],
            "date_publication": row[17],
            "date_creation": row[18],
            "date_modification": row[19],
            "categories_noms": row[20] or "",
        }
        articles.append(article)

    return articles


def obtenir_categorie_par_slug(slug):
    """Recupere une categorie par son slug."""
    requete = "SELECT * FROM categories WHERE slug = ? AND est_active = 1"
    row = executer_requete(requete, (slug,), fetchone=True)

    if not row:
        return None

    return {
        "id": row[0],
        "nom": row[1],
        "slug": row[2],
        "description": row[3],
        "icone": row[4],
        "ordre": row[5],
        "est_active": row[6],
        "date_creation": row[7],
        "date_modification": row[8],
    }


def incrementer_vues(article_id=None, livre_id=None):
    """Incremente le compteur de vues pour un article ou un livre."""
    from datetime import date

    aujourd_hui = date.today().isoformat()

    if article_id:
        requete_check = """
            SELECT id, nombre_vues FROM statistiques_vues
            WHERE article_id = ? AND date_vue = ?
        """
        existing = executer_requete(
            requete_check, (article_id, aujourd_hui), fetchone=True
        )

        if existing:
            requete_update = """
                UPDATE statistiques_vues SET nombre_vues = nombre_vues + 1
                WHERE id = ?
            """
            executer_requete(requete_update, (existing[0],), commit=True)
        else:
            requete_insert = """
                INSERT INTO statistiques_vues (article_id, nombre_vues, date_vue)
                VALUES (?, 1, ?)
            """
            executer_requete(requete_insert, (article_id, aujourd_hui), commit=True)

    elif livre_id:
        requete_check = """
            SELECT id, nombre_vues FROM statistiques_vues
            WHERE livre_id = ? AND date_vue = ?
        """
        existing = executer_requete(
            requete_check, (livre_id, aujourd_hui), fetchone=True
        )

        if existing:
            requete_update = """
                UPDATE statistiques_vues SET nombre_vues = nombre_vues + 1
                WHERE id = ?
            """
            executer_requete(requete_update, (existing[0],), commit=True)
        else:
            requete_insert = """
                INSERT INTO statistiques_vues (livre_id, nombre_vues, date_vue)
                VALUES (?, 1, ?)
            """
            executer_requete(requete_insert, (livre_id, aujourd_hui), commit=True)


def creer_article(donnees):
    """Crée un nouvel article."""
    requete = """
        INSERT INTO articles (
            titre, slug, contenu, extrait, type_article, image_url, banniere_url,
            auteur, temps_lecture, est_vedette, est_populaire, est_nouveau, est_publie,
            ordre_affichage, meta_keywords, meta_description, date_publication
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    parametres = (
        donnees["titre"],
        donnees["slug"],
        donnees["contenu"],
        donnees["extrait"],
        donnees["type_article"],
        donnees["image_url"],
        donnees["banniere_url"],
        donnees["auteur"],
        donnees["temps_lecture"],
        donnees["est_vedette"],
        donnees["est_populaire"],
        donnees["est_nouveau"],
        donnees["est_publie"],
        donnees.get("ordre_affichage", 0),
        donnees.get("meta_keywords"),
        donnees.get("meta_description"),
        donnees.get("date_publication"),
    )
    return executer_requete(requete, parametres, commit=True)


def modifier_article(article_id, donnees):
    """Modifie un article existant."""
    requete = """
        UPDATE articles SET
            titre = ?, slug = ?, contenu = ?, extrait = ?, type_article = ?,
            image_url = ?, banniere_url = ?, auteur = ?, temps_lecture = ?,
            est_vedette = ?, est_populaire = ?, est_nouveau = ?, est_publie = ?,
            ordre_affichage = ?, meta_keywords = ?, meta_description = ?,
            date_publication = ?
        WHERE id = ?
    """
    parametres = (
        donnees["titre"],
        donnees["slug"],
        donnees["contenu"],
        donnees["extrait"],
        donnees["type_article"],
        donnees["image_url"],
        donnees["banniere_url"],
        donnees["auteur"],
        donnees["temps_lecture"],
        donnees["est_vedette"],
        donnees["est_populaire"],
        donnees["est_nouveau"],
        donnees["est_publie"],
        donnees.get("ordre_affichage", 0),
        donnees.get("meta_keywords"),
        donnees.get("meta_description"),
        donnees.get("date_publication"),
        article_id,
    )
    executer_requete(requete, parametres, commit=True)


def supprimer_article(article_id):
    """Supprime un article."""
    requete = "DELETE FROM articles WHERE id = ?"
    executer_requete(requete, (article_id,), commit=True)


# =============================================================================
# OPÉRATIONS SUR LES LIVRES
# =============================================================================


def obtenir_tous_livres(
    limite=None, est_gratuit=None, est_vedette=None, est_publie=None
):
    """Récupère tous les livres avec filtres optionnels."""
    requete = """
        SELECT l.*, GROUP_CONCAT(c.nom) as categories_noms
        FROM livres l
        LEFT JOIN livre_categories lc ON l.id = lc.livre_id
        LEFT JOIN categories c ON lc.categorie_id = c.id
        WHERE 1=1
    """
    parametres = []

    if est_gratuit is not None:
        requete += " AND l.est_gratuit = ?"
        parametres.append(est_gratuit)

    if est_vedette is not None:
        requete += " AND l.est_vedette = ?"
        parametres.append(est_vedette)

    if est_publie is not None:
        requete += " AND l.est_publie = ?"
        parametres.append(est_publie)

    requete += " GROUP BY l.id ORDER BY l.ordre_affichage ASC, l.date_creation DESC"

    if limite:
        requete += " LIMIT ?"
        parametres.append(limite)

    resultats = executer_requete(requete, parametres, fetchall=True)

    livres = []
    for row in resultats:
        livre = {
            "id": row[0],
            "titre": row[1],
            "slug": row[2],
            "description": row[3],
            "extrait": row[4],
            "auteur": row[5],
            "co_auteurs": row[6],
            "isbn": row[7],
            "editeur": row[8],
            "annee_publication": row[9],
            "nombre_pages": row[10],
            "langue": row[11],
            "image_couverture": row[12],
            "fichier_pdf": row[13],
            "fichier_preview": row[14],
            "prix": row[15],
            "devise": row[16],
            "est_gratuit": row[17],
            "est_vedette": row[18],
            "est_nouveau": row[19],
            "est_publie": row[20],
            "ordre_affichage": row[21],
            "nombre_telechargements": row[22],
            "meta_keywords": row[23],
            "meta_description": row[24],
            "date_creation": row[25],
            "date_modification": row[26],
            "categories_noms": row[27] or "",
        }
        livres.append(livre)

    return livres


def obtenir_livre_par_id(livre_id):
    """Recupere un livre par son ID."""
    requete = """
        SELECT l.*, GROUP_CONCAT(c.nom) as categories_noms, GROUP_CONCAT(c.id) as categories_ids
        FROM livres l
        LEFT JOIN livre_categories lc ON l.id = lc.livre_id
        LEFT JOIN categories c ON lc.categorie_id = c.id
        WHERE l.id = ?
        GROUP BY l.id
    """
    row = executer_requete(requete, (livre_id,), fetchone=True)

    if not row:
        return None

    return {
        "id": row[0],
        "titre": row[1],
        "slug": row[2],
        "description": row[3],
        "extrait": row[4],
        "auteur": row[5],
        "co_auteurs": row[6],
        "isbn": row[7],
        "editeur": row[8],
        "annee_publication": row[9],
        "nombre_pages": row[10],
        "langue": row[11],
        "image_couverture": row[12],
        "fichier_pdf": row[13],
        "fichier_preview": row[14],
        "prix": row[15],
        "devise": row[16],
        "est_gratuit": row[17],
        "est_vedette": row[18],
        "est_nouveau": row[19],
        "est_publie": row[20],
        "ordre_affichage": row[21],
        "nombre_telechargements": row[22],
        "meta_keywords": row[23],
        "meta_description": row[24],
        "date_creation": row[25],
        "date_modification": row[26],
        "categories_noms": row[27] or "",
        "categories_ids": row[28] or "",
    }


def obtenir_livre_par_slug(slug):
    """Recupere un livre par son slug."""
    requete = """
        SELECT l.*, GROUP_CONCAT(c.nom) as categories_noms, GROUP_CONCAT(c.id) as categories_ids
        FROM livres l
        LEFT JOIN livre_categories lc ON l.id = lc.livre_id
        LEFT JOIN categories c ON lc.categorie_id = c.id
        WHERE l.slug = ? AND l.est_publie = 1
        GROUP BY l.id
    """
    row = executer_requete(requete, (slug,), fetchone=True)

    if not row:
        return None

    return {
        "id": row[0],
        "titre": row[1],
        "slug": row[2],
        "description": row[3],
        "extrait": row[4],
        "auteur": row[5],
        "co_auteurs": row[6],
        "isbn": row[7],
        "editeur": row[8],
        "annee_publication": row[9],
        "nombre_pages": row[10],
        "langue": row[11],
        "image_couverture": row[12],
        "fichier_pdf": row[13],
        "fichier_preview": row[14],
        "prix": row[15],
        "devise": row[16],
        "est_gratuit": row[17],
        "est_vedette": row[18],
        "est_nouveau": row[19],
        "est_publie": row[20],
        "ordre_affichage": row[21],
        "nombre_telechargements": row[22],
        "meta_keywords": row[23],
        "meta_description": row[24],
        "date_creation": row[25],
        "date_modification": row[26],
        "categories_noms": row[27] or "",
        "categories_ids": row[28] or "",
    }


def obtenir_livres_vedettes(limite=4):
    """Recupere les livres vedettes."""
    return obtenir_tous_livres(limite=limite, est_vedette=1, est_publie=1)


def obtenir_livres_nouveaux(limite=4):
    """Recupere les nouveaux livres."""
    requete = """
        SELECT l.*, GROUP_CONCAT(c.nom) as categories_noms
        FROM livres l
        LEFT JOIN livre_categories lc ON l.id = lc.livre_id
        LEFT JOIN categories c ON lc.categorie_id = c.id
        WHERE l.est_publie = 1 AND l.est_nouveau = 1
        GROUP BY l.id
        ORDER BY l.date_creation DESC
        LIMIT ?
    """
    resultats = executer_requete(requete, (limite,), fetchall=True)

    livres = []
    for row in resultats:
        livre = {
            "id": row[0],
            "titre": row[1],
            "slug": row[2],
            "description": row[3],
            "extrait": row[4],
            "auteur": row[5],
            "co_auteurs": row[6],
            "isbn": row[7],
            "editeur": row[8],
            "annee_publication": row[9],
            "nombre_pages": row[10],
            "langue": row[11],
            "image_couverture": row[12],
            "fichier_pdf": row[13],
            "fichier_preview": row[14],
            "prix": row[15],
            "devise": row[16],
            "est_gratuit": row[17],
            "est_vedette": row[18],
            "est_nouveau": row[19],
            "est_publie": row[20],
            "ordre_affichage": row[21],
            "nombre_telechargements": row[22],
            "meta_keywords": row[23],
            "meta_description": row[24],
            "date_creation": row[25],
            "date_modification": row[26],
            "categories_noms": row[27] or "",
        }
        livres.append(livre)

    return livres


def obtenir_livres_gratuits(limite=50):
    """Recupere les livres gratuits."""
    return obtenir_tous_livres(limite=limite, est_gratuit=1, est_publie=1)


def obtenir_livres_payants(limite=50):
    """Recupere les livres payants."""
    return obtenir_tous_livres(limite=limite, est_gratuit=0, est_publie=1)


def rechercher_livres(terme, limite=20):
    """Recherche des livres par terme."""
    requete = """
        SELECT l.*, GROUP_CONCAT(c.nom) as categories_noms
        FROM livres l
        LEFT JOIN livre_categories lc ON l.id = lc.livre_id
        LEFT JOIN categories c ON lc.categorie_id = c.id
        WHERE l.est_publie = 1
          AND (l.titre LIKE ? OR l.description LIKE ? OR l.auteur LIKE ?)
        GROUP BY l.id
        ORDER BY l.date_creation DESC
        LIMIT ?
    """
    pattern = f"%{terme}%"
    resultats = executer_requete(
        requete, (pattern, pattern, pattern, limite), fetchall=True
    )

    livres = []
    for row in resultats:
        livre = {
            "id": row[0],
            "titre": row[1],
            "slug": row[2],
            "description": row[3],
            "extrait": row[4],
            "auteur": row[5],
            "co_auteurs": row[6],
            "isbn": row[7],
            "editeur": row[8],
            "annee_publication": row[9],
            "nombre_pages": row[10],
            "langue": row[11],
            "image_couverture": row[12],
            "fichier_pdf": row[13],
            "fichier_preview": row[14],
            "prix": row[15],
            "devise": row[16],
            "est_gratuit": row[17],
            "est_vedette": row[18],
            "est_nouveau": row[19],
            "est_publie": row[20],
            "ordre_affichage": row[21],
            "nombre_telechargements": row[22],
            "meta_keywords": row[23],
            "meta_description": row[24],
            "date_creation": row[25],
            "date_modification": row[26],
            "categories_noms": row[27] or "",
        }
        livres.append(livre)

    return livres


def incrementer_telechargements(livre_id):
    """Incremente le compteur de telechargements d'un livre."""
    requete = "UPDATE livres SET nombre_telechargements = nombre_telechargements + 1 WHERE id = ?"
    executer_requete(requete, (livre_id,), commit=True)


def creer_livre(donnees):
    """Crée un nouveau livre."""
    requete = """
        INSERT INTO livres (
            titre, slug, description, extrait, auteur, co_auteurs, isbn, editeur,
            annee_publication, nombre_pages, langue, image_couverture, fichier_pdf,
            fichier_preview, prix, devise, est_gratuit, est_vedette, est_nouveau,
            est_publie, ordre_affichage, nombre_telechargements, meta_keywords, meta_description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    parametres = (
        donnees["titre"],
        donnees["slug"],
        donnees["description"],
        donnees["extrait"],
        donnees["auteur"],
        donnees["co_auteurs"],
        donnees["isbn"],
        donnees["editeur"],
        donnees["annee_publication"],
        donnees["nombre_pages"],
        donnees["langue"],
        donnees["image_couverture"],
        donnees["fichier_pdf"],
        donnees["fichier_preview"],
        donnees["prix"],
        donnees["devise"],
        donnees["est_gratuit"],
        donnees["est_vedette"],
        donnees["est_nouveau"],
        donnees["est_publie"],
        donnees.get("ordre_affichage", 0),
        donnees.get("nombre_telechargements", 0),
        donnees.get("meta_keywords"),
        donnees.get("meta_description"),
    )
    return executer_requete(requete, parametres, commit=True)


def modifier_livre(livre_id, donnees):
    """Modifie un livre existant."""
    requete = """
        UPDATE livres SET
            titre = ?, slug = ?, description = ?, extrait = ?, auteur = ?, co_auteurs = ?,
            isbn = ?, editeur = ?, annee_publication = ?, nombre_pages = ?, langue = ?,
            image_couverture = ?, fichier_pdf = ?, fichier_preview = ?, prix = ?, devise = ?,
            est_gratuit = ?, est_vedette = ?, est_nouveau = ?, est_publie = ?,
            ordre_affichage = ?, nombre_telechargements = ?, meta_keywords = ?, meta_description = ?
        WHERE id = ?
    """
    parametres = (
        donnees["titre"],
        donnees["slug"],
        donnees["description"],
        donnees["extrait"],
        donnees["auteur"],
        donnees["co_auteurs"],
        donnees["isbn"],
        donnees["editeur"],
        donnees["annee_publication"],
        donnees["nombre_pages"],
        donnees["langue"],
        donnees["image_couverture"],
        donnees["fichier_pdf"],
        donnees["fichier_preview"],
        donnees["prix"],
        donnees["devise"],
        donnees["est_gratuit"],
        donnees["est_vedette"],
        donnees["est_nouveau"],
        donnees["est_publie"],
        donnees.get("ordre_affichage", 0),
        donnees.get("nombre_telechargements", 0),
        donnees.get("meta_keywords"),
        donnees.get("meta_description"),
        livre_id,
    )
    executer_requete(requete, parametres, commit=True)


def supprimer_livre(livre_id):
    """Supprime un livre."""
    requete = "DELETE FROM livres WHERE id = ?"
    executer_requete(requete, (livre_id,), commit=True)


# =============================================================================
# OPÉRATIONS SUR LES ACHATS
# =============================================================================


def obtenir_tous_achats(limite=None, statut=None):
    """Récupère tous les achats avec filtres optionnels."""
    requete = """
        SELECT a.*, l.titre as livre_titre
        FROM achats a
        JOIN livres l ON a.livre_id = l.id
        WHERE 1=1
    """
    parametres = []

    if statut:
        requete += " AND a.statut = ?"
        parametres.append(statut)

    requete += " ORDER BY a.date_achat DESC"

    if limite:
        requete += " LIMIT ?"
        parametres.append(limite)

    resultats = executer_requete(requete, parametres, fetchall=True)

    achats = []
    for row in resultats:
        achat = {
            "id": row[0],
            "livre_id": row[1],
            "nom_client": row[2],
            "email_client": row[3],
            "telephone_client": row[4],
            "montant": row[5],
            "devise": row[6],
            "methode_paiement": row[7],
            "reference_transaction": row[8],
            "statut": row[9],
            "token_telechargement": row[10],
            "nombre_telechargements": row[11],
            "max_telechargements": row[12],
            "expire_le": row[13],
            "notes": row[14],
            "date_achat": row[15],
            "livre_titre": row[16],
        }
        achats.append(achat)

    return achats


def obtenir_achat_par_id(achat_id):
    """Récupère un achat par son ID."""
    requete = """
        SELECT a.*, l.titre as livre_titre, l.fichier_pdf
        FROM achats a
        JOIN livres l ON a.livre_id = l.id
        WHERE a.id = ?
    """
    row = executer_requete(requete, (achat_id,), fetchone=True)

    if not row:
        return None

    return {
        "id": row[0],
        "livre_id": row[1],
        "nom_client": row[2],
        "email_client": row[3],
        "telephone_client": row[4],
        "montant": row[5],
        "devise": row[6],
        "methode_paiement": row[7],
        "reference_transaction": row[8],
        "statut": row[9],
        "token_telechargement": row[10],
        "nombre_telechargements": row[11],
        "max_telechargements": row[12],
        "expire_le": row[13],
        "notes": row[14],
        "date_achat": row[15],
        "livre_titre": row[16],
        "fichier_pdf": row[17],
    }


def modifier_statut_achat(achat_id, nouveau_statut, reference=None):
    """Modifie le statut d'un achat et genere un token si paye."""
    import secrets
    from datetime import datetime, timedelta

    if nouveau_statut == "paye":
        token = secrets.token_urlsafe(32)
        expire_le = (datetime.now() + timedelta(days=7)).isoformat()

        requete = """
            UPDATE achats SET
                statut = ?,
                reference_transaction = ?,
                token_telechargement = ?,
                expire_le = ?
            WHERE id = ?
        """
        executer_requete(
            requete,
            (nouveau_statut, reference, token, expire_le, achat_id),
            commit=True,
        )
    else:
        requete = "UPDATE achats SET statut = ? WHERE id = ?"
        executer_requete(requete, (nouveau_statut, achat_id), commit=True)


def creer_achat(donnees):
    """Cree un nouvel achat."""
    requete = """
        INSERT INTO achats (
            livre_id, nom_client, email_client, telephone_client,
            montant, devise, statut
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    parametres = (
        donnees["livre_id"],
        donnees["nom_client"],
        donnees["email_client"],
        donnees.get("telephone_client", ""),
        donnees["montant"],
        donnees.get("devise", "CFA"),
        donnees.get("statut", "en_attente"),
    )
    return executer_requete(requete, parametres, commit=True)


def obtenir_achat_par_token(token):
    """Recupere un achat par son token de telechargement."""
    requete = """
        SELECT a.*, l.titre as livre_titre, l.fichier_pdf, l.slug as livre_slug
        FROM achats a
        JOIN livres l ON a.livre_id = l.id
        WHERE a.token_telechargement = ?
    """
    row = executer_requete(requete, (token,), fetchone=True)

    if not row:
        return None

    return {
        "id": row[0],
        "livre_id": row[1],
        "nom_client": row[2],
        "email_client": row[3],
        "telephone_client": row[4],
        "montant": row[5],
        "devise": row[6],
        "methode_paiement": row[7],
        "reference_transaction": row[8],
        "statut": row[9],
        "token_telechargement": row[10],
        "nombre_telechargements": row[11],
        "max_telechargements": row[12],
        "expire_le": row[13],
        "notes": row[14],
        "date_achat": row[15],
        "livre_titre": row[16],
        "fichier_pdf": row[17],
        "livre_slug": row[18],
    }


def verifier_achat_valide(token):
    """Verifie si un achat est valide pour le telechargement."""
    from datetime import datetime

    achat = obtenir_achat_par_token(token)

    if not achat:
        return None

    if achat["statut"] != "paye":
        return None

    if achat["nombre_telechargements"] >= achat["max_telechargements"]:
        return None

    if achat["expire_le"]:
        try:
            expire_dt = datetime.fromisoformat(achat["expire_le"])
            if datetime.now() > expire_dt:
                return None
        except (ValueError, TypeError):
            pass

    return achat


def incrementer_telechargement_achat(achat_id):
    """Incremente le compteur de telechargements d'un achat."""
    requete = "UPDATE achats SET nombre_telechargements = nombre_telechargements + 1 WHERE id = ?"
    executer_requete(requete, (achat_id,), commit=True)


def enregistrer_telechargement(livre_id, achat_id=None, ip=None, user_agent=None):
    """Enregistre un telechargement dans l'historique."""
    requete = """
        INSERT INTO telechargements (livre_id, achat_id, ip_address, user_agent)
        VALUES (?, ?, ?, ?)
    """
    executer_requete(requete, (livre_id, achat_id, ip, user_agent), commit=True)


# =============================================================================
# OPÉRATIONS SUR LES MESSAGES
# =============================================================================


def obtenir_messages_contact(limite=None, est_lu=None):
    """Récupère les messages de contact."""
    requete = "SELECT * FROM messages_contact WHERE 1=1"
    parametres = []

    if est_lu is not None:
        requete += " AND est_lu = ?"
        parametres.append(est_lu)

    requete += " ORDER BY date_creation DESC"

    if limite:
        requete += " LIMIT ?"
        parametres.append(limite)

    resultats = executer_requete(requete, parametres, fetchall=True)

    messages = []
    for row in resultats:
        message = {
            "id": row[0],
            "nom": row[1],
            "email": row[2],
            "sujet": row[3],
            "message": row[4],
            "est_lu": row[5],
            "date_creation": row[6],
        }
        messages.append(message)

    return messages


def marquer_message_lu(message_id):
    """Marque un message comme lu."""
    requete = "UPDATE messages_contact SET est_lu = 1 WHERE id = ?"
    executer_requete(requete, (message_id,), commit=True)


# =============================================================================
# OPÉRATIONS SUR LA NEWSLETTER
# =============================================================================


def obtenir_abonnes_newsletter():
    """Récupère tous les abonnés à la newsletter."""
    requete = "SELECT * FROM abonnes_newsletter WHERE est_actif = 1 ORDER BY date_inscription DESC"
    resultats = executer_requete(requete, fetchall=True)

    abonnes = []
    for row in resultats:
        abonne = {
            "id": row[0],
            "email": row[1],
            "nom": row[2],
            "est_actif": row[3],
            "date_inscription": row[4],
        }
        abonnes.append(abonne)

    return abonnes


# =============================================================================
# OPÉRATIONS SUR LES CATÉGORIES
# =============================================================================


def obtenir_toutes_categories():
    """Récupère toutes les catégories actives."""
    requete = (
        "SELECT * FROM categories WHERE est_active = 1 ORDER BY ordre ASC, nom ASC"
    )
    resultats = executer_requete(requete, fetchall=True)

    categories = []
    for row in resultats:
        categorie = {
            "id": row[0],
            "nom": row[1],
            "slug": row[2],
            "description": row[3],
            "icone": row[4],
            "ordre": row[5],
            "est_active": row[6],
            "date_creation": row[7],
            "date_modification": row[8],
        }
        categories.append(categorie)

    return categories


def associer_categories(contenu_id, categorie_ids):
    """Associe des catégories à un article."""
    # Supprimer les associations existantes
    requete_delete = "DELETE FROM article_categories WHERE article_id = ?"
    executer_requete(requete_delete, (contenu_id,), commit=True)

    # Ajouter les nouvelles associations
    if categorie_ids:
        requete_insert = (
            "INSERT INTO article_categories (article_id, categorie_id) VALUES (?, ?)"
        )
        for cat_id in categorie_ids:
            executer_requete(requete_insert, (contenu_id, cat_id), commit=True)


def associer_categories_livre(livre_id, categorie_ids):
    """Associe des catégories à un livre."""
    # Supprimer les associations existantes
    requete_delete = "DELETE FROM livre_categories WHERE livre_id = ?"
    executer_requete(requete_delete, (livre_id,), commit=True)

    # Ajouter les nouvelles associations
    if categorie_ids:
        requete_insert = (
            "INSERT INTO livre_categories (livre_id, categorie_id) VALUES (?, ?)"
        )
        for cat_id in categorie_ids:
            executer_requete(requete_insert, (livre_id, cat_id), commit=True)


# =============================================================================
# STATISTIQUES ET CONFIGURATION
# =============================================================================


def obtenir_statistiques_globales():
    """Récupère les statistiques globales du site."""
    stats = {}

    # Nombre total d'articles
    requete = "SELECT COUNT(*) FROM articles WHERE est_publie = 1"
    stats["total_articles"] = executer_requete(requete, fetchone=True)[0]

    # Nombre total de livres
    requete = "SELECT COUNT(*) FROM livres WHERE est_publie = 1"
    stats["total_livres"] = executer_requete(requete, fetchone=True)[0]

    # Nombre total de catégories
    requete = "SELECT COUNT(*) FROM categories WHERE est_active = 1"
    stats["total_categories"] = executer_requete(requete, fetchone=True)[0]

    # Nombre total d'achats
    requete = "SELECT COUNT(*) FROM achats"
    stats["total_achats"] = executer_requete(requete, fetchone=True)[0]

    # Nombre de messages non lus
    requete = "SELECT COUNT(*) FROM messages_contact WHERE est_lu = 0"
    stats["messages_non_lus"] = executer_requete(requete, fetchone=True)[0]

    # Nombre d'abonnés newsletter
    requete = "SELECT COUNT(*) FROM abonnes_newsletter WHERE est_actif = 1"
    stats["total_abonnes"] = executer_requete(requete, fetchone=True)[0]

    # Revenus totaux
    requete = "SELECT SUM(montant) FROM achats WHERE statut = 'paye'"
    result = executer_requete(requete, fetchone=True)[0]
    stats["revenus_totaux"] = result if result else 0

    # Nombre total de vues
    requete = "SELECT SUM(nombre_vues) FROM statistiques_vues"
    result = executer_requete(requete, fetchone=True)[0]
    stats["total_vues"] = result if result else 0

    # Nombre total de lecteurs (abonnés newsletter actifs)
    requete = "SELECT COUNT(*) FROM abonnes_newsletter WHERE est_actif = 1"
    stats["total_lecteurs"] = executer_requete(requete, fetchone=True)[0]

    return stats


def obtenir_toutes_configurations():
    """Récupère toutes les configurations du site."""
    requete = "SELECT cle, valeur FROM configuration_site"
    resultats = executer_requete(requete, fetchall=True)

    config = {}
    for row in resultats:
        config[row[0]] = row[1]

    return config


def modifier_configuration(cle, valeur):
    """Modifie une configuration."""
    requete = "UPDATE configuration_site SET valeur = ? WHERE cle = ?"
    executer_requete(requete, (valeur, cle), commit=True)


# =============================================================================
# RECHERCHE GLOBALE
# =============================================================================


def rechercher_global(terme, limite=50):
    """Recherche globale dans les articles et les livres."""
    articles = rechercher_articles(terme, limite=limite)
    livres = rechercher_livres(terme, limite=limite)

    return {
        "articles": articles,
        "livres": livres,
        "total": len(articles) + len(livres),
    }


# =============================================================================
# NEWSLETTER
# =============================================================================


def inscrire_newsletter(email, nom=None):
    """Inscrit un email a la newsletter."""
    requete_check = "SELECT id FROM abonnes_newsletter WHERE email = ?"
    existing = executer_requete(requete_check, (email,), fetchone=True)

    if existing:
        return False

    requete = "INSERT INTO abonnes_newsletter (email, nom) VALUES (?, ?)"
    executer_requete(requete, (email, nom), commit=True)
    return True


# =============================================================================
# MESSAGES DE CONTACT
# =============================================================================


def creer_message_contact(donnees):
    """Cree un nouveau message de contact."""
    requete = """
        INSERT INTO messages_contact (nom, email, sujet, message)
        VALUES (?, ?, ?, ?)
    """
    parametres = (
        donnees["nom"],
        donnees["email"],
        donnees.get("sujet", ""),
        donnees["message"],
    )
    return executer_requete(requete, parametres, commit=True)
