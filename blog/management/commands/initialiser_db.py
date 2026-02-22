"""
Commande personnalisée pour initialiser la base de données.

Cette commande crée les tables et insère les données initiales
sans utiliser les migrations Django (SQL brut).

Usage:
    python manage.py initialiser_db
    python manage.py initialiser_db --demo  # Avec données de démo
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import sqlite3


class Command(BaseCommand):
    help = 'Initialise la base de données avec le schéma SQL et les données'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Inclure les données de démonstration',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Supprimer les données existantes avant l\'initialisation',
        )
    
    def handle(self, *args, **options):
        from blog.db_schema import (
            SCHEMA_SQL,
            DONNEES_INITIALES_SQL,
            DONNEES_DEMO_SQL
        )
        
        chemin_db = settings.DATABASES['default']['NAME']
        self.stdout.write(f"Initialisation de la base de données: {chemin_db}")
        
        try:
            conn = sqlite3.connect(chemin_db)
            curseur = conn.cursor()
            
            # Option de reset
            if options['reset']:
                self.stdout.write(self.style.WARNING('Suppression des tables existantes...'))
                tables = [
                    'statistiques_vues',
                    'contenu_categories',
                    'contenus',
                    'categories',
                    'liens_footer',
                    'configuration_site',
                    'reseaux_sociaux',
                ]
                for table in tables:
                    curseur.execute(f"DROP TABLE IF EXISTS {table}")
                conn.commit()
            
            # Création du schéma
            self.stdout.write('Création des tables...')
            curseur.executescript(SCHEMA_SQL)
            conn.commit()
            self.stdout.write(self.style.SUCCESS('✓ Tables créées avec succès'))
            
            # Données initiales
            self.stdout.write('Insertion des données initiales...')
            curseur.executescript(DONNEES_INITIALES_SQL)
            conn.commit()
            self.stdout.write(self.style.SUCCESS('✓ Données initiales insérées'))
            
            # Données de démonstration
            if options['demo']:
                self.stdout.write('Insertion des données de démonstration...')
                curseur.executescript(DONNEES_DEMO_SQL)
                conn.commit()
                self.stdout.write(self.style.SUCCESS('✓ Données de démonstration insérées'))
            
            # Afficher les statistiques
            curseur.execute("SELECT COUNT(*) FROM categories")
            nb_categories = curseur.fetchone()[0]
            
            curseur.execute("SELECT COUNT(*) FROM contenus")
            nb_contenus = curseur.fetchone()[0]
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('═' * 50))
            self.stdout.write(self.style.SUCCESS('Base de données initialisée avec succès!'))
            self.stdout.write(f'  • {nb_categories} catégories')
            self.stdout.write(f'  • {nb_contenus} contenus')
            self.stdout.write(self.style.SUCCESS('═' * 50))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur: {str(e)}'))
            raise
        finally:
            conn.close()
