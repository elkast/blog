"""
Configuration de l'interface d'administration pour le Blog Académique du Professeur.
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages

from blog.db_operations import (
    # Articles
    obtenir_tous_articles,
    obtenir_article_par_id,
    creer_article,
    modifier_article,
    supprimer_article,
    # Livres
    obtenir_tous_livres,
    obtenir_livre_par_id,
    creer_livre,
    modifier_livre,
    supprimer_livre,
    associer_categories_livre,
    # Achats
    obtenir_tous_achats,
    obtenir_achat_par_id,
    modifier_statut_achat,
    # Messages
    obtenir_messages_contact,
    marquer_message_lu,
    # Newsletter
    obtenir_abonnes_newsletter,
    # Catégories et stats
    obtenir_toutes_categories,
    associer_categories,
    obtenir_statistiques_globales,
    obtenir_toutes_configurations,
    modifier_configuration,
)


class ProfesseurBlogAdminSite(AdminSite):
    """Site d'administration personnalisé pour le Blog du Professeur."""

    site_header = "📚 Blog Académique - Administration"
    site_title = "Blog Professeur Admin"
    index_title = "Tableau de bord"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # Dashboard
            path("", self.admin_view(self.tableau_bord), name="index"),
            # Articles
            path(
                "articles/", self.admin_view(self.liste_articles), name="contenus_liste"
            ),
            path(
                "articles/ajouter/",
                self.admin_view(self.ajouter_article),
                name="contenus_ajouter",
            ),
            path(
                "articles/<int:article_id>/modifier/",
                self.admin_view(self.modifier_article_vue),
                name="contenus_modifier",
            ),
            path(
                "articles/<int:article_id>/supprimer/",
                self.admin_view(self.supprimer_article_vue),
                name="contenus_supprimer",
            ),
            # Livres
            path("livres/", self.admin_view(self.liste_livres), name="livres_liste"),
            path(
                "livres/ajouter/",
                self.admin_view(self.ajouter_livre),
                name="livres_ajouter",
            ),
            path(
                "livres/<int:livre_id>/modifier/",
                self.admin_view(self.modifier_livre_vue),
                name="livres_modifier",
            ),
            path(
                "livres/<int:livre_id>/supprimer/",
                self.admin_view(self.supprimer_livre_vue),
                name="livres_supprimer",
            ),
            # Achats
            path("achats/", self.admin_view(self.liste_achats), name="achats_liste"),
            path(
                "achats/<int:achat_id>/",
                self.admin_view(self.detail_achat),
                name="achats_detail",
            ),
            # Messages
            path(
                "messages/", self.admin_view(self.liste_messages), name="messages_liste"
            ),
            path(
                "messages/<int:message_id>/lu/",
                self.admin_view(self.marquer_lu),
                name="messages_lu",
            ),
            # Newsletter
            path(
                "newsletter/",
                self.admin_view(self.liste_abonnes),
                name="newsletter_liste",
            ),
            # Configuration
            path(
                "configuration/",
                self.admin_view(self.configuration),
                name="configuration",
            ),
        ]
        return custom_urls + urls

    # =========================================================================
    # TABLEAU DE BORD
    # =========================================================================

    def tableau_bord(self, request):
        stats = obtenir_statistiques_globales()
        derniers_articles = obtenir_tous_articles(limite=5)
        derniers_livres = obtenir_tous_livres(limite=5)
        derniers_achats = obtenir_tous_achats(limite=5)
        messages_recents = obtenir_messages_contact(limite=5)

        context = {
            **self.each_context(request),
            "title": "Tableau de bord",
            "stats": stats,
            "derniers_contenus": derniers_articles,
            "derniers_livres": derniers_livres,
            "derniers_achats": derniers_achats,
            "messages_recents": messages_recents,
        }
        return render(request, "admin/tableau_bord.html", context)

    # =========================================================================
    # GESTION DES ARTICLES
    # =========================================================================

    def liste_articles(self, request):
        type_filtre = request.GET.get("type")
        articles = obtenir_tous_articles(type_article=type_filtre, limite=100)
        context = {
            **self.each_context(request),
            "title": "Gestion des articles",
            "contenus": articles,
            "type_filtre": type_filtre,
            "types_disponibles": ["article", "publication", "recherche", "actualite"],
        }
        return render(request, "admin/contenus_liste.html", context)

    def ajouter_article(self, request):
        categories = obtenir_toutes_categories()
        erreurs = {}
        donnees = {
            "titre": "",
            "slug": "",
            "contenu": "",
            "extrait": "",
            "type_article": "article",
            "temps_lecture": "",
            "image_url": "",
            "banniere_url": "",
            "auteur": "Professeur",
            "est_vedette": 0,
            "est_populaire": 0,
            "est_nouveau": 0,
            "est_publie": 0,
        }

        if request.method == "POST":
            titre = request.POST.get("titre", "").strip()
            slug = request.POST.get("slug", "").strip()

            # Générer automatiquement le slug si vide, ou nettoyer le slug fourni
            if titre:
                if not slug:
                    import re

                    slug = re.sub(r"[^a-zA-Z0-9]+", "-", titre).strip("-").lower()
                else:
                    # Nettoyer le slug fourni pour s'assurer qu'il est valide
                    import re

                    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", slug).strip("-").lower()

            donnees = {
                "titre": titre,
                "slug": slug,
                "contenu": request.POST.get("contenu", "").strip(),
                "extrait": request.POST.get("extrait", "").strip(),
                "type_article": request.POST.get("type_article", "article"),
                "temps_lecture": request.POST.get("temps_lecture") or None,
                "image_url": request.POST.get("image_url", "").strip(),
                "banniere_url": request.POST.get("banniere_url", "").strip(),
                "auteur": request.POST.get("auteur", "Professeur").strip(),
                "est_vedette": 1 if request.POST.get("est_vedette") else 0,
                "est_populaire": 1 if request.POST.get("est_populaire") else 0,
                "est_nouveau": 1 if request.POST.get("est_nouveau") else 0,
                "est_publie": 1 if request.POST.get("est_publie") else 0,
            }

            if not donnees["titre"]:
                erreurs["titre"] = "Le titre est requis."
            if not donnees["slug"]:
                erreurs["slug"] = "Le slug est requis."

            if not erreurs:
                try:
                    if donnees["temps_lecture"]:
                        donnees["temps_lecture"] = int(donnees["temps_lecture"])
                    article_id = creer_article(donnees)
                    cat_ids = request.POST.getlist("categories")
                    if cat_ids:
                        associer_categories(article_id, [int(c) for c in cat_ids])
                    messages.success(request, f'Article "{donnees["titre"]}" créé!')
                    return redirect("admin:contenus_liste")
                except Exception as e:
                    messages.error(request, f"Erreur: {str(e)}")

        context = {
            **self.each_context(request),
            "title": "Ajouter un article",
            "categories": categories,
            "erreurs": erreurs,
            "donnees": donnees,
            "contenu": None,
            "types_disponibles": ["article", "publication", "recherche", "actualite"],
        }
        return render(request, "admin/contenus_form.html", context)

    def modifier_article_vue(self, request, article_id):
        article = obtenir_article_par_id(article_id)
        if not article:
            messages.error(request, "Article non trouvé.")
            return redirect("admin:contenus_liste")

        categories = obtenir_toutes_categories()
        erreurs = {}

        if request.method == "POST":
            donnees = {
                "titre": request.POST.get("titre", "").strip(),
                "slug": request.POST.get("slug", "").strip(),
                "contenu": request.POST.get("contenu", "").strip(),
                "extrait": request.POST.get("extrait", "").strip(),
                "type_article": request.POST.get("type_article", "article"),
                "temps_lecture": request.POST.get("temps_lecture") or None,
                "image_url": request.POST.get("image_url", "").strip(),
                "banniere_url": request.POST.get("banniere_url", "").strip(),
                "auteur": request.POST.get("auteur", "Professeur").strip(),
                "est_vedette": 1 if request.POST.get("est_vedette") else 0,
                "est_populaire": 1 if request.POST.get("est_populaire") else 0,
                "est_nouveau": 1 if request.POST.get("est_nouveau") else 0,
                "est_publie": 1 if request.POST.get("est_publie") else 0,
            }

            if not donnees["titre"]:
                erreurs["titre"] = "Le titre est requis."

            if not erreurs:
                try:
                    if donnees["temps_lecture"]:
                        donnees["temps_lecture"] = int(donnees["temps_lecture"])
                    modifier_article(article_id, donnees)
                    cat_ids = request.POST.getlist("categories")
                    associer_categories(
                        article_id, [int(c) for c in cat_ids] if cat_ids else []
                    )
                    messages.success(request, f"Article modifié!")
                    return redirect("admin:contenus_liste")
                except Exception as e:
                    messages.error(request, f"Erreur: {str(e)}")
            article = donnees

        context = {
            **self.each_context(request),
            "title": f'Modifier: {article["titre"]}',
            "contenu": article,
            "categories": categories,
            "erreurs": erreurs,
            "mode_edition": True,
            "types_disponibles": ["article", "publication", "recherche", "actualite"],
        }
        return render(request, "admin/contenus_form.html", context)

    def supprimer_article_vue(self, request, article_id):
        article = obtenir_article_par_id(article_id)
        if not article:
            messages.error(request, "Article non trouvé.")
            return redirect("admin:contenus_liste")

        if request.method == "POST":
            try:
                supprimer_article(article_id)
                messages.success(request, f"Article supprimé!")
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
            return redirect("admin:contenus_liste")

        context = {
            **self.each_context(request),
            "title": f'Supprimer: {article["titre"]}',
            "contenu": article,
        }
        return render(request, "admin/contenus_supprimer.html", context)

    # =========================================================================
    # GESTION DES LIVRES
    # =========================================================================

    def liste_livres(self, request):
        filtre = request.GET.get("filtre")
        if filtre == "gratuit":
            livres = obtenir_tous_livres(est_gratuit=True, limite=100)
        elif filtre == "payant":
            livres = obtenir_tous_livres(est_gratuit=False, limite=100)
        else:
            livres = obtenir_tous_livres(limite=100)

        context = {
            **self.each_context(request),
            "title": "Gestion des livres",
            "livres": livres,
            "filtre": filtre,
        }
        return render(request, "admin/livres_liste.html", context)

    def ajouter_livre(self, request):
        categories = obtenir_toutes_categories()
        erreurs = {}
        donnees = {
            "titre": "",
            "slug": "",
            "description": "",
            "extrait": "",
            "auteur": "Mr Talnan",
            "co_auteurs": "",
            "isbn": "",
            "editeur": "",
            "annee_publication": None,
            "nombre_pages": None,
            "langue": "Français",
            "image_couverture": "",
            "fichier_pdf": "",
            "fichier_preview": "",
            "prix": 0,
            "devise": "FCFA",
            "est_gratuit": 0,
            "est_vedette": 0,
            "est_nouveau": 0,
            "est_publie": 0,
        }

        if request.method == "POST":
            donnees = {
                "titre": request.POST.get("titre", "").strip(),
                "slug": request.POST.get("slug", "").strip(),
                "description": request.POST.get("description", "").strip(),
                "extrait": request.POST.get("extrait", "").strip(),
                "auteur": request.POST.get("auteur", "Professeur").strip(),
                "co_auteurs": request.POST.get("co_auteurs", "").strip(),
                "isbn": request.POST.get("isbn", "").strip(),
                "editeur": request.POST.get("editeur", "").strip(),
                "annee_publication": request.POST.get("annee_publication") or None,
                "nombre_pages": request.POST.get("nombre_pages") or None,
                "langue": request.POST.get("langue", "Français").strip(),
                "image_couverture": request.POST.get("image_couverture", "").strip(),
                "fichier_pdf": request.POST.get("fichier_pdf", "").strip(),
                "fichier_preview": request.POST.get("fichier_preview", "").strip(),
                "prix": request.POST.get("prix") or 0,
                "devise": request.POST.get("devise", "CFA"),
                "est_gratuit": 1 if request.POST.get("est_gratuit") else 0,
                "est_vedette": 1 if request.POST.get("est_vedette") else 0,
                "est_nouveau": 1 if request.POST.get("est_nouveau") else 0,
                "est_publie": 1 if request.POST.get("est_publie") else 0,
            }

            if not donnees["titre"]:
                erreurs["titre"] = "Le titre est requis."
            if not donnees["slug"]:
                erreurs["slug"] = "Le slug est requis."

            if not erreurs:
                try:
                    if donnees["annee_publication"]:
                        donnees["annee_publication"] = int(donnees["annee_publication"])
                    if donnees["nombre_pages"]:
                        donnees["nombre_pages"] = int(donnees["nombre_pages"])
                    if donnees["prix"]:
                        donnees["prix"] = float(donnees["prix"])

                    livre_id = creer_livre(donnees)
                    cat_ids = request.POST.getlist("categories")
                    if cat_ids:
                        associer_categories_livre(livre_id, [int(c) for c in cat_ids])
                    messages.success(request, f'Livre "{donnees["titre"]}" créé!')
                    return redirect("admin:livres_liste")
                except Exception as e:
                    messages.error(request, f"Erreur: {str(e)}")

        context = {
            **self.each_context(request),
            "title": "Ajouter un livre",
            "categories": categories,
            "erreurs": erreurs,
            "donnees": donnees,
            "livre": donnees,
        }
        return render(request, "admin/livres_form.html", context)

    def modifier_livre_vue(self, request, livre_id):
        livre = obtenir_livre_par_id(livre_id)
        if not livre:
            messages.error(request, "Livre non trouvé.")
            return redirect("admin:livres_liste")

        categories = obtenir_toutes_categories()
        erreurs = {}

        if request.method == "POST":
            donnees = {
                "titre": request.POST.get("titre", "").strip(),
                "slug": request.POST.get("slug", "").strip(),
                "description": request.POST.get("description", "").strip(),
                "extrait": request.POST.get("extrait", "").strip(),
                "auteur": request.POST.get("auteur", "Professeur").strip(),
                "co_auteurs": request.POST.get("co_auteurs", "").strip(),
                "isbn": request.POST.get("isbn", "").strip(),
                "editeur": request.POST.get("editeur", "").strip(),
                "annee_publication": request.POST.get("annee_publication") or None,
                "nombre_pages": request.POST.get("nombre_pages") or None,
                "langue": request.POST.get("langue", "Français").strip(),
                "image_couverture": request.POST.get("image_couverture", "").strip(),
                "fichier_pdf": request.POST.get("fichier_pdf", "").strip(),
                "fichier_preview": request.POST.get("fichier_preview", "").strip(),
                "prix": request.POST.get("prix") or 0,
                "devise": request.POST.get("devise", "CFA"),
                "est_gratuit": 1 if request.POST.get("est_gratuit") else 0,
                "est_vedette": 1 if request.POST.get("est_vedette") else 0,
                "est_nouveau": 1 if request.POST.get("est_nouveau") else 0,
                "est_publie": 1 if request.POST.get("est_publie") else 0,
            }

            if not donnees["titre"]:
                erreurs["titre"] = "Le titre est requis."

            if not erreurs:
                try:
                    if donnees["annee_publication"]:
                        donnees["annee_publication"] = int(donnees["annee_publication"])
                    if donnees["nombre_pages"]:
                        donnees["nombre_pages"] = int(donnees["nombre_pages"])
                    if donnees["prix"]:
                        donnees["prix"] = float(donnees["prix"])

                    modifier_livre(livre_id, donnees)
                    cat_ids = request.POST.getlist("categories")
                    associer_categories_livre(
                        livre_id, [int(c) for c in cat_ids] if cat_ids else []
                    )
                    messages.success(request, f"Livre modifié!")
                    return redirect("admin:livres_liste")
                except Exception as e:
                    messages.error(request, f"Erreur: {str(e)}")
            livre = donnees

        context = {
            **self.each_context(request),
            "title": f'Modifier: {livre["titre"]}',
            "livre": livre,
            "donnees": livre,
            "categories": categories,
            "erreurs": erreurs,
            "mode_edition": True,
        }
        return render(request, "admin/livres_form.html", context)

    def supprimer_livre_vue(self, request, livre_id):
        livre = obtenir_livre_par_id(livre_id)
        if not livre:
            messages.error(request, "Livre non trouvé.")
            return redirect("admin:livres_liste")

        if request.method == "POST":
            try:
                supprimer_livre(livre_id)
                messages.success(request, f"Livre supprimé!")
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
            return redirect("admin:livres_liste")

        context = {
            **self.each_context(request),
            "title": f'Supprimer: {livre["titre"]}',
            "livre": livre,
        }
        return render(request, "admin/livres_supprimer.html", context)

    # =========================================================================
    # GESTION DES ACHATS
    # =========================================================================

    def liste_achats(self, request):
        statut = request.GET.get("statut")
        achats = obtenir_tous_achats(statut=statut, limite=100)
        context = {
            **self.each_context(request),
            "title": "Gestion des achats",
            "achats": achats,
            "statut_filtre": statut,
        }
        return render(request, "admin/achats_liste.html", context)

    def detail_achat(self, request, achat_id):
        achat = obtenir_achat_par_id(achat_id)
        if not achat:
            messages.error(request, "Achat non trouvé.")
            return redirect("admin:achats_liste")

        if request.method == "POST":
            nouveau_statut = request.POST.get("statut")
            if nouveau_statut:
                modifier_statut_achat(achat_id, nouveau_statut)
                messages.success(request, "Statut mis à jour!")
                return redirect("admin:achats_liste")

        context = {
            **self.each_context(request),
            "title": f"Achat #{achat_id}",
            "achat": achat,
        }
        return render(request, "admin/achats_detail.html", context)

    # =========================================================================
    # GESTION DES MESSAGES
    # =========================================================================

    def liste_messages(self, request):
        est_lu = request.GET.get("lu")
        if est_lu == "1":
            msgs = obtenir_messages_contact(est_lu=True, limite=100)
        elif est_lu == "0":
            msgs = obtenir_messages_contact(est_lu=False, limite=100)
        else:
            msgs = obtenir_messages_contact(limite=100)

        context = {
            **self.each_context(request),
            "title": "Messages de contact",
            "messages_liste": msgs,
            "filtre_lu": est_lu,
        }
        return render(request, "admin/messages_liste.html", context)

    def marquer_lu(self, request, message_id):
        marquer_message_lu(message_id)
        messages.success(request, "Message marqué comme lu.")
        return redirect("admin:messages_liste")

    # =========================================================================
    # NEWSLETTER
    # =========================================================================

    def liste_abonnes(self, request):
        abonnes = obtenir_abonnes_newsletter()
        context = {
            **self.each_context(request),
            "title": "Abonnés Newsletter",
            "abonnes": abonnes,
        }
        return render(request, "admin/newsletter_liste.html", context)

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    def configuration(self, request):
        config = obtenir_toutes_configurations()

        if request.method == "POST":
            for cle in config.keys():
                nouvelle_valeur = request.POST.get(cle, "")
                if nouvelle_valeur != config.get(cle, ""):
                    modifier_configuration(cle, nouvelle_valeur)
            messages.success(request, "Configuration mise à jour!")
            return redirect("admin:configuration")

        context = {
            **self.each_context(request),
            "title": "Configuration du site",
            "config": config,
        }
        return render(request, "admin/configuration.html", context)


# Créer l'instance du site admin
admin_site = ProfesseurBlogAdminSite(name="professeur_admin")

# Enregistrer les modèles Django par défaut
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
