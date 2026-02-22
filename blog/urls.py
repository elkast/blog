"""
Configuration des URLs pour le Blog Académique du Professeur.
"""

from django.urls import path
from blog import views

app_name = "blog"

urlpatterns = [
    # Page d'accueil
    path("", views.accueil, name="accueil"),
    # Articles
    path("articles/", views.liste_articles, name="liste_articles"),
    path("publications/", views.liste_publications, name="liste_publications"),
    path("recherches/", views.liste_recherches, name="liste_recherches"),
    path("article/<str:slug>/", views.detail_article, name="detail_article"),
    path("categorie/<str:slug>/", views.categorie, name="categorie"),
    # Livres
    path("livres/", views.liste_livres, name="liste_livres"),
    path("livre/<str:slug>/", views.detail_livre, name="detail_livre"),
    path("livre/<str:slug>/acheter/", views.acheter_livre, name="acheter_livre"),
    path(
        "livre/<str:slug>/telecharger/",
        views.telecharger_livre_gratuit,
        name="telecharger_livre_gratuit",
    ),
    path("paiement/<int:achat_id>/", views.paiement_livre, name="paiement_livre"),
    path(
        "confirmation/<str:token>/", views.confirmation_achat, name="confirmation_achat"
    ),
    path("telecharger/<str:token>/", views.telecharger_livre, name="telecharger_livre"),
    # Recherche
    path("recherche/", views.recherche, name="recherche"),
    # API
    path("api/recherche/", views.api_recherche, name="api_recherche"),
    path("api/newsletter/", views.api_newsletter, name="api_newsletter"),
    # Pages statiques
    path("a-propos/", views.a_propos, name="a_propos"),
    path("cv/", views.cv, name="cv"),
    path("contact/", views.contact, name="contact"),
    path("confidentialite/", views.confidentialite, name="confidentialite"),
    path("mentions-legales/", views.conditions, name="conditions"),
]
