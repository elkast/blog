"""
Commande de gestion pour initialiser la base de données du Blog Médical.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import sqlite3


class Command(BaseCommand):
    help = 'Initialise la base de données avec le schéma et les données de démonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Ajoute les données de démonstration',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Supprime les tables existantes avant de les recréer',
        )

    def handle(self, *args, **options):
        from blog.db_schema import SCHEMA_SQL, DONNEES_INITIALES_SQL, DONNEES_DEMO_SQL
        
        chemin_db = settings.DATABASES['default']['NAME']
        self.stdout.write(f'Base de données: {chemin_db}')
        
        connexion = sqlite3.connect(chemin_db)
        curseur = connexion.cursor()
        
        try:
            if options['reset']:
                self.stdout.write('Suppression des tables existantes...')
                tables = [
                    'statistiques_vues',
                    'article_categories',
                    'articles',
                    'services',
                    'categories',
                    'liens_footer',
                    'configuration_site',
                    'reseaux_sociaux',
                    'rendez_vous',
                    'messages_contact',
                    # anciennes tables
                    'contenu_categories',
                    'contenus',
                ]
                for table in tables:
                    try:
                        curseur.execute(f'DROP TABLE IF EXISTS {table}')
                    except Exception:
                        pass
                connexion.commit()
                self.stdout.write(self.style.SUCCESS('Tables supprimées.'))
            
            # Créer le schéma
            self.stdout.write('Création du schéma...')
            curseur.executescript(SCHEMA_SQL)
            connexion.commit()
            self.stdout.write(self.style.SUCCESS('Schéma créé avec succès.'))
            
            # Insérer les données initiales
            self.stdout.write('Insertion des données initiales...')
            curseur.executescript(DONNEES_INITIALES_SQL)
            connexion.commit()
            self.stdout.write(self.style.SUCCESS('Données initiales insérées.'))
            
            # Données de démo si demandé
            if options['demo']:
                self.stdout.write('Insertion des données de démonstration...')
                curseur.executescript(DONNEES_DEMO_SQL)
                connexion.commit()
                self.stdout.write(self.style.SUCCESS('Données de démonstration insérées.'))
            
            self.stdout.write(self.style.SUCCESS('✅ Base de données initialisée avec succès!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur: {e}'))
            connexion.rollback()
            raise
        finally:
            connexion.close()
