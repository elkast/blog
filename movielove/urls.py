"""
Configuration des URLs pour le projet Blog Académique.

Ce fichier définit les routes principales du projet.
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importer notre site admin personnalisé
from blog.admin import admin_site

# Gestionnaires d'erreurs personnalisés
handler404 = 'blog.views.erreur_404'
handler500 = 'blog.views.erreur_500'

urlpatterns = [
    # Administration Django personnalisée
    path('admin/', admin_site.urls),
    
    # Application Blog
    path('', include('blog.urls')),
]

# Servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
