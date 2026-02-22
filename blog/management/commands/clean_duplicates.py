"""
Commande Django pour nettoyer les doublons dans la base de données.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from blog.db_operations import (
    obtenir_tous_articles,
    obtenir_tous_livres,
    supprimer_article,
    supprimer_livre,
)


class Command(BaseCommand):
    help = "Nettoie les doublons dans la base de données (articles et livres)"

    def handle(self, *args, **options):
        self.stdout.write("Début du nettoyage des doublons...\n")

        # Nettoyer les doublons d'articles
        self.clean_articles_duplicates()

        # Nettoyer les doublons de livres
        self.clean_books_duplicates()

        self.stdout.write(self.style.SUCCESS("Nettoyage des doublons terminé!"))

    def clean_articles_duplicates(self):
        """Nettoie les doublons d'articles basés sur le titre et le slug."""
        self.stdout.write("Nettoyage des doublons d'articles...")

        with connection.cursor() as cursor:
            # Trouver les doublons d'articles par titre
            cursor.execute(
                """
                SELECT titre, COUNT(*) as count
                FROM articles
                GROUP BY titre
                HAVING COUNT(*) > 1
            """
            )

            duplicates = cursor.fetchall()

            if not duplicates:
                self.stdout.write("Aucun doublon d'articles trouvé.")
                return

            for title, count in duplicates:
                self.stdout.write(f'Doublon trouvé: "{title}" ({count} occurrences)')

                # Garder seulement le premier article (celui avec l'ID le plus petit)
                cursor.execute(
                    """
                    DELETE FROM articles
                    WHERE titre = %s AND id NOT IN (
                        SELECT MIN(id) FROM articles WHERE titre = %s
                    )
                """,
                    [title, title],
                )

                self.stdout.write(f'  Supprimé {count-1} doublon(s) pour "{title}"')

    def clean_books_duplicates(self):
        """Nettoie les doublons de livres basés sur le titre et le slug."""
        self.stdout.write("Nettoyage des doublons de livres...")

        with connection.cursor() as cursor:
            # Trouver les doublons de livres par titre
            cursor.execute(
                """
                SELECT titre, COUNT(*) as count
                FROM livres
                GROUP BY titre
                HAVING COUNT(*) > 1
            """
            )

            duplicates = cursor.fetchall()

            if not duplicates:
                self.stdout.write("Aucun doublon de livres trouvé.")
                return

            for title, count in duplicates:
                self.stdout.write(f'Doublon trouvé: "{title}" ({count} occurrences)')

                # Garder seulement le premier livre (celui avec l'ID le plus petit)
                cursor.execute(
                    """
                    DELETE FROM livres
                    WHERE titre = %s AND id NOT IN (
                        SELECT MIN(id) FROM livres WHERE titre = %s
                    )
                """,
                    [title, title],
                )

                self.stdout.write(f'  Supprimé {count-1} doublon(s) pour "{title}"')

    def clean_articles_duplicates_by_slug(self):
        """Nettoie les doublons d'articles basés sur le slug."""
        self.stdout.write("Nettoyage des doublons d'articles par slug...")

        with connection.cursor() as cursor:
            # Trouver les doublons d'articles par slug
            cursor.execute(
                """
                SELECT slug, COUNT(*) as count
                FROM articles
                GROUP BY slug
                HAVING COUNT(*) > 1
            """
            )

            duplicates = cursor.fetchall()

            for slug, count in duplicates:
                self.stdout.write(
                    f'Doublon de slug trouvé: "{slug}" ({count} occurrences)'
                )

                # Garder seulement le premier article
                cursor.execute(
                    """
                    DELETE FROM articles
                    WHERE slug = %s AND id NOT IN (
                        SELECT MIN(id) FROM articles WHERE slug = %s
                    )
                """,
                    [slug, slug],
                )

                self.stdout.write(
                    f'  Supprimé {count-1} doublon(s) pour le slug "{slug}"'
                )

    def clean_books_duplicates_by_slug(self):
        """Nettoie les doublons de livres basés sur le slug."""
        self.stdout.write("Nettoyage des doublons de livres par slug...")

        with connection.cursor() as cursor:
            # Trouver les doublons de livres par slug
            cursor.execute(
                """
                SELECT slug, COUNT(*) as count
                FROM livres
                GROUP BY slug
                HAVING COUNT(*) > 1
            """
            )

            duplicates = cursor.fetchall()

            for slug, count in duplicates:
                self.stdout.write(
                    f'Doublon de slug trouvé: "{slug}" ({count} occurrences)'
                )

                # Garder seulement le premier livre
                cursor.execute(
                    """
                    DELETE FROM livres
                    WHERE slug = %s AND id NOT IN (
                        SELECT MIN(id) FROM livres WHERE slug = %s
                    )
                """,
                    [slug, slug],
                )

                self.stdout.write(
                    f'  Supprimé {count-1} doublon(s) pour le slug "{slug}"'
                )
