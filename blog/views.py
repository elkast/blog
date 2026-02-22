"""
Vues pour le Blog Académique du Professeur.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404, FileResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib import messages

from blog.db_operations import (
    # Articles
    obtenir_tous_articles,
    obtenir_article_par_slug,
    obtenir_articles_vedettes,
    obtenir_articles_populaires,
    obtenir_articles_plus_lus,
    obtenir_derniers_articles,
    rechercher_articles,
    obtenir_articles_par_categorie,
    obtenir_categorie_par_slug,
    obtenir_toutes_categories,
    incrementer_vues,
    # Livres
    obtenir_tous_livres,
    obtenir_livre_par_slug,
    obtenir_livres_vedettes,
    obtenir_livres_nouveaux,
    obtenir_livres_gratuits,
    obtenir_livres_payants,
    rechercher_livres,
    incrementer_telechargements,
    # Achats
    creer_achat,
    obtenir_achat_par_token,
    verifier_achat_valide,
    incrementer_telechargement_achat,
    enregistrer_telechargement,
    # Autres
    rechercher_global,
    inscrire_newsletter,
    creer_message_contact,
    obtenir_toutes_configurations,
    obtenir_statistiques_globales,
)


# =============================================================================
# PAGES PRINCIPALES
# =============================================================================


@require_GET
def accueil(request):
    """Page d'accueil du blog académique."""
    contexte = {
        "titre_page": "Accueil",
        "articles_vedettes": obtenir_articles_vedettes(),
        "contenus_vedettes": obtenir_articles_vedettes(),
        "articles_populaires": obtenir_articles_populaires(limite=6),
        "derniers_articles": obtenir_derniers_articles(limite=6),
        "articles_plus_lus": obtenir_articles_plus_lus(limite=6),
        "livres_vedettes": obtenir_livres_vedettes(limite=4),
        "livres_nouveaux": obtenir_livres_nouveaux(limite=4),
        "config_site": obtenir_toutes_configurations(),
    }
    return render(request, "blog/accueil.html", contexte)


# =============================================================================
# ARTICLES
# =============================================================================


@require_GET
def liste_articles(request):
    """Page listant tous les articles."""
    page = request.GET.get("page", 1)
    categorie = request.GET.get("categorie")
    type_article = request.GET.get("type")

    if categorie:
        articles = obtenir_articles_par_categorie(categorie, limite=100)
        titre = f"Articles - {categorie.replace('-', ' ').title()}"
    elif type_article:
        articles = obtenir_tous_articles(type_article=type_article, limite=100)
        titre = f"Articles - {type_article.title()}"
    else:
        articles = obtenir_tous_articles(limite=100)
        titre = "Tous les Articles"

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(page)

    # Récupérer les catégories pour les filtres
    categories = obtenir_toutes_categories()

    contexte = {
        "titre_page": titre,
        "contenus": page_obj,
        "type_contenu": "article",
        "categories": categories,
    }
    return render(request, "blog/liste_contenus.html", contexte)


@require_GET
def liste_publications(request):
    """Page listant toutes les publications académiques."""
    page = request.GET.get("page", 1)
    publications = obtenir_tous_articles(type_article="publication", limite=100)

    paginator = Paginator(publications, 12)
    page_obj = paginator.get_page(page)

    contexte = {
        "titre_page": "Publications Académiques",
        "contenus": page_obj,
        "type_contenu": "publication",
    }
    return render(request, "blog/liste_contenus.html", contexte)


@require_GET
def liste_recherches(request):
    """Page listant les travaux de recherche."""
    page = request.GET.get("page", 1)
    recherches = obtenir_tous_articles(type_article="recherche", limite=100)

    paginator = Paginator(recherches, 12)
    page_obj = paginator.get_page(page)

    contexte = {
        "titre_page": "Travaux de Recherche",
        "contenus": page_obj,
        "type_contenu": "recherche",
    }
    return render(request, "blog/liste_contenus.html", contexte)


@require_GET
def detail_article(request, slug):
    """Page de détail d'un article."""
    article = obtenir_article_par_slug(slug)

    if not article:
        raise Http404("Cet article n'existe pas.")

    incrementer_vues(article_id=article["id"])

    similaires = obtenir_articles_populaires(limite=6)
    similaires = [s for s in similaires if s["id"] != article["id"]][:5]

    contexte = {
        "titre_page": article["titre"],
        "contenu": article,
        "similaires": similaires,
    }
    return render(request, "blog/detail_contenu.html", contexte)


@require_GET
def categorie(request, slug):
    """Page listant les articles d'une catégorie."""
    cat = obtenir_categorie_par_slug(slug)

    if not cat:
        raise Http404("Cette catégorie n'existe pas.")

    page = request.GET.get("page", 1)
    articles = obtenir_articles_par_categorie(slug, limite=100)

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(page)

    contexte = {
        "titre_page": cat["nom"],
        "categorie": cat,
        "contenus": page_obj,
    }
    return render(request, "blog/categorie.html", contexte)


# =============================================================================
# LIVRES
# =============================================================================


@require_GET
def liste_livres(request):
    """Page listant tous les livres."""
    page = request.GET.get("page", 1)

    # Filtres
    est_gratuit = request.GET.get("gratuit")
    est_nouveau = request.GET.get("nouveau")

    if est_gratuit == "1":
        livres = obtenir_livres_gratuits(limite=50)
        titre = "Livres Gratuits"
    elif est_gratuit == "0":
        livres = obtenir_livres_payants(limite=50)
        titre = "Livres Payants"
    elif est_nouveau == "1":
        livres = obtenir_livres_nouveaux(limite=50)
        titre = "Nouveautés"
    else:
        livres = obtenir_tous_livres(limite=50)
        titre = "Tous les Livres"

    paginator = Paginator(livres, 12)
    page_obj = paginator.get_page(page)

    contexte = {
        "titre_page": titre,
        "livres": page_obj,
        "filtre_gratuit": est_gratuit,
        "filtre_nouveau": est_nouveau,
    }
    return render(request, "blog/liste_livres.html", contexte)


@require_GET
def detail_livre(request, slug):
    """Page de détail d'un livre."""
    livre = obtenir_livre_par_slug(slug)

    if not livre:
        raise Http404("Ce livre n'existe pas.")

    incrementer_vues(livre_id=livre["id"])

    autres_livres = obtenir_livres_vedettes(limite=4)
    autres_livres = [l for l in autres_livres if l["id"] != livre["id"]][:3]

    contexte = {
        "titre_page": livre["titre"],
        "livre": livre,
        "autres_livres": autres_livres,
    }
    return render(request, "blog/detail_livre.html", contexte)


def acheter_livre(request, slug):
    """Page d'achat d'un livre."""
    livre = obtenir_livre_par_slug(slug)

    if not livre:
        raise Http404("Ce livre n'existe pas.")

    if livre["est_gratuit"]:
        return redirect("blog:telecharger_livre_gratuit", slug=slug)

    erreurs = {}

    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        email = request.POST.get("email", "").strip()
        telephone = request.POST.get("telephone", "").strip()

        if not nom:
            erreurs["nom"] = "Le nom est requis."
        if not email:
            erreurs["email"] = "L'email est requis."

        if not erreurs:
            # Créer l'achat en attente
            achat_id = creer_achat(
                {
                    "livre_id": livre["id"],
                    "nom_client": nom,
                    "email_client": email,
                    "telephone_client": telephone,
                    "montant": livre["prix"],
                    "devise": livre["devise"],
                    "statut": "en_attente",
                }
            )

            # Rediriger vers la page de paiement (simulation)
            return redirect("blog:paiement_livre", achat_id=achat_id)

    contexte = {
        "titre_page": f"Acheter: {livre['titre']}",
        "livre": livre,
        "erreurs": erreurs,
    }
    return render(request, "blog/acheter_livre.html", contexte)


def paiement_livre(request, achat_id):
    """Page de paiement (simulation)."""
    from blog.db_operations import obtenir_achat_par_id, modifier_statut_achat

    achat = obtenir_achat_par_id(achat_id)
    if not achat:
        raise Http404("Achat non trouvé.")

    if request.method == "POST":
        # Simulation du paiement réussi
        import secrets

        reference = f"PAY-{secrets.token_hex(8).upper()}"
        modifier_statut_achat(achat_id, "paye", reference)

        messages.success(request, "Paiement effectué avec succès!")

        # Récupérer l'achat mis à jour avec le token
        achat = obtenir_achat_par_id(achat_id)
        return redirect("blog:confirmation_achat", token=achat["token_telechargement"])

    contexte = {
        "titre_page": "Paiement",
        "achat": achat,
    }
    return render(request, "blog/paiement_livre.html", contexte)


@require_GET
def confirmation_achat(request, token):
    """Page de confirmation après achat."""
    achat = obtenir_achat_par_token(token)

    if not achat:
        raise Http404("Achat non trouvé.")

    contexte = {
        "titre_page": "Confirmation d'achat",
        "achat": achat,
        "token": token,
    }
    return render(request, "blog/confirmation_achat.html", contexte)


@require_GET
def telecharger_livre(request, token):
    """Téléchargement d'un livre payant."""
    achat = verifier_achat_valide(token)

    if not achat:
        messages.error(request, "Lien de téléchargement invalide ou expiré.")
        return redirect("blog:accueil")

    # Incrémenter le compteur de téléchargement
    incrementer_telechargement_achat(achat["id"])
    incrementer_telechargements(achat["livre_id"])
    enregistrer_telechargement(
        livre_id=achat["livre_id"],
        achat_id=achat["id"],
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT"),
    )

    # Rediriger vers le fichier PDF (ou servir le fichier)
    if achat["fichier_pdf"]:
        # En production, servir le fichier sécurisé
        return redirect(achat["fichier_pdf"])

    messages.info(request, "Fichier non disponible pour le moment.")
    return redirect("blog:detail_livre", slug=achat["livre_slug"])


@require_GET
def telecharger_livre_gratuit(request, slug):
    """Téléchargement d'un livre gratuit."""
    livre = obtenir_livre_par_slug(slug)

    if not livre:
        raise Http404("Ce livre n'existe pas.")

    if not livre["est_gratuit"]:
        return redirect("blog:acheter_livre", slug=slug)

    # Incrémenter les téléchargements
    incrementer_telechargements(livre["id"])
    enregistrer_telechargement(
        livre_id=livre["id"],
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT"),
    )

    if livre["fichier_pdf"]:
        return redirect(livre["fichier_pdf"])

    messages.info(request, "Fichier non disponible pour le moment.")
    return redirect("blog:detail_livre", slug=slug)


# =============================================================================
# RECHERCHE
# =============================================================================


@require_GET
def recherche(request):
    """Page de résultats de recherche globale."""
    terme = request.GET.get("q", "").strip()
    resultats = {"articles": [], "livres": [], "total": 0}

    if terme and len(terme) >= 2:
        resultats = rechercher_global(terme, limite=50)

    contexte = {
        "titre_page": f"Recherche : {terme}" if terme else "Recherche",
        "terme_recherche": terme,
        "resultats": resultats,
        "nombre_resultats": resultats["total"],
    }
    return render(request, "blog/recherche.html", contexte)


# =============================================================================
# API
# =============================================================================


@require_GET
def api_recherche(request):
    """API de recherche en temps réel."""
    terme = request.GET.get("q", "").strip()

    if len(terme) < 2:
        return JsonResponse({"resultats": []})

    articles = rechercher_articles(terme, limite=5)
    livres = rechercher_livres(terme, limite=5)

    data = []

    for r in articles:
        data.append(
            {
                "id": r["id"],
                "titre": r["titre"],
                "type": "article",
                "sous_type": r["type_article"],
                "image": r["image_url"],
                "slug": r["slug"],
                "url": f"/article/{r['slug']}/",
            }
        )

    for r in livres:
        data.append(
            {
                "id": r["id"],
                "titre": r["titre"],
                "type": "livre",
                "image": r["image_couverture"],
                "slug": r["slug"],
                "url": f"/livre/{r['slug']}/",
                "prix": r["prix"] if not r["est_gratuit"] else "Gratuit",
            }
        )

    return JsonResponse({"resultats": data})


@csrf_exempt
@require_POST
def api_newsletter(request):
    """API pour inscription newsletter."""
    import json

    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip()
        nom = data.get("nom", "").strip()

        if not email:
            return JsonResponse(
                {"success": False, "message": "Email requis"}, status=400
            )

        if inscrire_newsletter(email, nom):
            return JsonResponse({"success": True, "message": "Inscription réussie!"})
        else:
            return JsonResponse({"success": False, "message": "Déjà inscrit"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# =============================================================================
# PAGES STATIQUES
# =============================================================================


@require_GET
def a_propos(request):
    """Page À propos du professeur."""
    config = obtenir_toutes_configurations()
    contexte = {
        "titre_page": "À propos",
        "config": config,
    }
    return render(request, "blog/pages/a_propos.html", contexte)


@require_GET
def cv(request):
    """Page CV et parcours."""
    config = obtenir_toutes_configurations()
    contexte = {
        "titre_page": "CV & Parcours",
        "config": config,
    }
    return render(request, "blog/pages/cv.html", contexte)


def contact(request):
    """Page de contact."""
    erreurs = {}
    succes = False

    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        email = request.POST.get("email", "").strip()
        sujet = request.POST.get("sujet", "").strip()
        message = request.POST.get("message", "").strip()

        if not nom:
            erreurs["nom"] = "Le nom est requis."
        if not email:
            erreurs["email"] = "L'email est requis."
        if not message:
            erreurs["message"] = "Le message est requis."

        if not erreurs:
            creer_message_contact(
                {
                    "nom": nom,
                    "email": email,
                    "sujet": sujet,
                    "message": message,
                }
            )
            succes = True
            messages.success(request, "Votre message a été envoyé!")

    contexte = {
        "titre_page": "Contact",
        "erreurs": erreurs,
        "succes": succes,
    }
    return render(request, "blog/pages/contact.html", contexte)


@require_GET
def confidentialite(request):
    return render(
        request,
        "blog/pages/confidentialite.html",
        {"titre_page": "Politique de confidentialité"},
    )


@require_GET
def conditions(request):
    return render(
        request, "blog/pages/conditions.html", {"titre_page": "Mentions légales"}
    )


# =============================================================================
# PAGES D'ERREUR
# =============================================================================


def erreur_404(request, exception):
    return render(
        request, "blog/erreurs/404.html", {"titre_page": "Page non trouvée"}, status=404
    )


def erreur_500(request):
    return render(
        request, "blog/erreurs/500.html", {"titre_page": "Erreur serveur"}, status=500
    )
