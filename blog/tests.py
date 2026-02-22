"""
Tests unitaires et d'intégration pour le Blog Académique.

Ce module contient tous les tests pour valider le bon fonctionnement
de l'application Blog.

Exécution des tests:
    python manage.py test blog
    python manage.py test blog.tests.TestsBaseDeDonnees
    pytest blog/tests.py -v
"""

import sqlite3
from unittest import TestCase
from django.test import TestCase as DjangoTestCase, Client
from django.urls import reverse
from django.conf import settings


# =============================================================================
# TESTS UNITAIRES - BASE DE DONNÉES
# =============================================================================

class TestsBaseDeDonnees(TestCase):
    """Tests pour les opérations de base de données."""
    
    @classmethod
    def setUpClass(cls):
        """Initialise une base de données de test."""
        super().setUpClass()
        cls.chemin_db = ':memory:'
        cls.conn = sqlite3.connect(cls.chemin_db)
        cls.conn.row_factory = sqlite3.Row
        
        # Créer les tables
        from blog.db_schema import SCHEMA_SQL
        cls.conn.executescript(SCHEMA_SQL)
        cls.conn.commit()
    
    @classmethod
    def tearDownClass(cls):
        """Ferme la connexion."""
        super().tearDownClass()
        cls.conn.close()
    
    def test_creation_categorie(self):
        """Teste la création d'une catégorie."""
        curseur = self.conn.cursor()
        curseur.execute(
            "INSERT INTO categories (nom, slug, description) VALUES (?, ?, ?)",
            ('Test', 'test', 'Description test')
        )
        self.conn.commit()
        
        curseur.execute("SELECT * FROM categories WHERE slug = 'test'")
        categorie = curseur.fetchone()
        
        self.assertIsNotNone(categorie)
        self.assertEqual(categorie['nom'], 'Test')
        self.assertEqual(categorie['slug'], 'test')
    
    def test_creation_contenu(self):
        """Teste la création d'un contenu."""
        curseur = self.conn.cursor()
        curseur.execute("""
            INSERT INTO contenus (titre, slug, type_contenu, annee, note)
            VALUES (?, ?, ?, ?, ?)
        """, ('Film Test', 'film-test', 'film', 2024, 4.5))
        self.conn.commit()
        
        curseur.execute("SELECT * FROM contenus WHERE slug = 'film-test'")
        contenu = curseur.fetchone()
        
        self.assertIsNotNone(contenu)
        self.assertEqual(contenu['titre'], 'Film Test')
        self.assertEqual(contenu['type_contenu'], 'film')
        self.assertEqual(contenu['annee'], 2024)
        self.assertEqual(contenu['note'], 4.5)
    
    def test_contrainte_type_contenu(self):
        """Teste la contrainte sur le type de contenu."""
        curseur = self.conn.cursor()
        
        with self.assertRaises(sqlite3.IntegrityError):
            curseur.execute("""
                INSERT INTO contenus (titre, slug, type_contenu)
                VALUES (?, ?, ?)
            """, ('Invalid', 'invalid', 'invalid_type'))
            self.conn.commit()
    
    def test_contrainte_note(self):
        """Teste la contrainte sur la note (0-5)."""
        curseur = self.conn.cursor()
        
        with self.assertRaises(sqlite3.IntegrityError):
            curseur.execute("""
                INSERT INTO contenus (titre, slug, type_contenu, note)
                VALUES (?, ?, ?, ?)
            """, ('Invalid', 'invalid-note', 'film', 10))
            self.conn.commit()
    
    def test_slug_unique(self):
        """Teste l'unicité du slug."""
        curseur = self.conn.cursor()
        curseur.execute("""
            INSERT INTO contenus (titre, slug, type_contenu)
            VALUES (?, ?, ?)
        """, ('Premier', 'slug-unique', 'film'))
        self.conn.commit()
        
        with self.assertRaises(sqlite3.IntegrityError):
            curseur.execute("""
                INSERT INTO contenus (titre, slug, type_contenu)
                VALUES (?, ?, ?)
            """, ('Deuxième', 'slug-unique', 'film'))
            self.conn.commit()


# =============================================================================
# TESTS UNITAIRES - FONCTIONS D'ACCÈS AUX DONNÉES
# =============================================================================

class TestsFonctionsAccesDonnees(DjangoTestCase):
    """Tests pour les fonctions d'accès aux données."""
    
    @classmethod
    def setUpClass(cls):
        """Initialise la base de données de test."""
        super().setUpClass()
        from blog.db_schema import SCHEMA_SQL, DONNEES_INITIALES_SQL
        
        chemin_db = settings.DATABASES['default']['NAME']
        conn = sqlite3.connect(chemin_db)
        conn.executescript(SCHEMA_SQL)
        conn.executescript(DONNEES_INITIALES_SQL)
        conn.commit()
        conn.close()
    
    def test_obtenir_toutes_categories(self):
        """Teste la récupération de toutes les catégories."""
        from blog.db_operations import obtenir_toutes_categories
        
        categories = obtenir_toutes_categories()
        
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        
        # Vérifier la structure
        premiere = categories[0]
        self.assertIn('nom', premiere)
        self.assertIn('slug', premiere)
    
    def test_obtenir_configuration(self):
        """Teste la récupération d'une configuration."""
        from blog.db_operations import obtenir_configuration
        
        nom_site = obtenir_configuration('nom_site', 'Défaut')
        
        self.assertEqual(nom_site, 'Movie Love')
    
    def test_obtenir_configuration_defaut(self):
        """Teste la valeur par défaut si clé inexistante."""
        from blog.db_operations import obtenir_configuration
        
        valeur = obtenir_configuration('cle_inexistante', 'valeur_defaut')
        
        self.assertEqual(valeur, 'valeur_defaut')
    
    def test_ligne_vers_dict(self):
        """Teste la conversion ligne vers dictionnaire."""
        from blog.db_operations import ligne_vers_dict
        
        # Test avec None
        resultat = ligne_vers_dict(None)
        self.assertIsNone(resultat)


# =============================================================================
# TESTS D'INTÉGRATION - VUES
# =============================================================================

class TestsVuesIntegration(DjangoTestCase):
    """Tests d'intégration pour les vues."""
    
    @classmethod
    def setUpClass(cls):
        """Initialise la base de données avec des données de démo."""
        super().setUpClass()
        from blog.db_schema import SCHEMA_SQL, DONNEES_INITIALES_SQL, DONNEES_DEMO_SQL
        
        chemin_db = settings.DATABASES['default']['NAME']
        conn = sqlite3.connect(chemin_db)
        conn.executescript(SCHEMA_SQL)
        conn.executescript(DONNEES_INITIALES_SQL)
        conn.executescript(DONNEES_DEMO_SQL)
        conn.commit()
        conn.close()
    
    def setUp(self):
        """Initialise le client de test."""
        self.client = Client()
    
    def test_accueil_status_200(self):
        """Teste que la page d'accueil retourne 200."""
        response = self.client.get(reverse('blog:accueil'))
        self.assertEqual(response.status_code, 200)
    
    def test_accueil_contient_elements(self):
        """Teste que la page d'accueil contient les éléments attendus."""
        response = self.client.get(reverse('blog:accueil'))
        
        self.assertContains(response, 'Movie love')
        self.assertContains(response, 'Most Viewed')
    
    def test_liste_films_status_200(self):
        """Teste que la page des films retourne 200."""
        response = self.client.get(reverse('blog:liste_films'))
        self.assertEqual(response.status_code, 200)
    
    def test_liste_series_status_200(self):
        """Teste que la page des séries retourne 200."""
        response = self.client.get(reverse('blog:liste_series'))
        self.assertEqual(response.status_code, 200)
    
    def test_recherche_status_200(self):
        """Teste que la page de recherche retourne 200."""
        response = self.client.get(reverse('blog:recherche'))
        self.assertEqual(response.status_code, 200)
    
    def test_recherche_avec_terme(self):
        """Teste la recherche avec un terme."""
        response = self.client.get(reverse('blog:recherche'), {'q': 'Raya'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Raya')
    
    def test_detail_contenu_existant(self):
        """Teste l'affichage d'un contenu existant."""
        response = self.client.get(
            reverse('blog:detail_contenu', args=['raya-dernier-dragon'])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_detail_contenu_inexistant_404(self):
        """Teste qu'un contenu inexistant retourne 404."""
        response = self.client.get(
            reverse('blog:detail_contenu', args=['contenu-inexistant'])
        )
        self.assertEqual(response.status_code, 404)
    
    def test_categorie_existante(self):
        """Teste l'affichage d'une catégorie existante."""
        response = self.client.get(
            reverse('blog:categorie', args=['action'])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_categorie_inexistante_404(self):
        """Teste qu'une catégorie inexistante retourne 404."""
        response = self.client.get(
            reverse('blog:categorie', args=['categorie-inexistante'])
        )
        self.assertEqual(response.status_code, 404)
    
    def test_pages_statiques(self):
        """Teste les pages statiques."""
        pages = ['a_propos', 'contact', 'confidentialite', 'conditions']
        
        for page in pages:
            response = self.client.get(reverse(f'blog:{page}'))
            self.assertEqual(
                response.status_code, 200,
                f"La page {page} devrait retourner 200"
            )


# =============================================================================
# TESTS API
# =============================================================================

class TestsAPI(DjangoTestCase):
    """Tests pour les endpoints API."""
    
    @classmethod
    def setUpClass(cls):
        """Initialise la base de données."""
        super().setUpClass()
        from blog.db_schema import SCHEMA_SQL, DONNEES_INITIALES_SQL, DONNEES_DEMO_SQL
        
        chemin_db = settings.DATABASES['default']['NAME']
        conn = sqlite3.connect(chemin_db)
        conn.executescript(SCHEMA_SQL)
        conn.executescript(DONNEES_INITIALES_SQL)
        conn.executescript(DONNEES_DEMO_SQL)
        conn.commit()
        conn.close()
    
    def setUp(self):
        self.client = Client()
    
    def test_api_recherche_json(self):
        """Teste que l'API recherche retourne du JSON."""
        response = self.client.get(
            reverse('blog:api_recherche'),
            {'q': 'Avatar'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('resultats', data)
    
    def test_api_recherche_terme_court(self):
        """Teste que l'API ignore les termes trop courts."""
        response = self.client.get(
            reverse('blog:api_recherche'),
            {'q': 'a'}
        )
        
        data = response.json()
        self.assertEqual(data['resultats'], [])
    
    def test_api_populaires_json(self):
        """Teste que l'API populaires retourne du JSON."""
        response = self.client.get(reverse('blog:api_populaires'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('contenus', data)
    
    def test_api_populaires_filtre_type(self):
        """Teste le filtrage par type."""
        response = self.client.get(
            reverse('blog:api_populaires'),
            {'type': 'film'}
        )
        
        data = response.json()
        
        # Vérifier que des résultats sont retournés
        self.assertIsInstance(data['contenus'], list)


# =============================================================================
# TESTS DE PERFORMANCE
# =============================================================================

class TestsPerformance(DjangoTestCase):
    """Tests de performance basiques."""
    
    @classmethod
    def setUpClass(cls):
        """Initialise la base de données."""
        super().setUpClass()
        from blog.db_schema import SCHEMA_SQL, DONNEES_INITIALES_SQL, DONNEES_DEMO_SQL
        
        chemin_db = settings.DATABASES['default']['NAME']
        conn = sqlite3.connect(chemin_db)
        conn.executescript(SCHEMA_SQL)
        conn.executescript(DONNEES_INITIALES_SQL)
        conn.executescript(DONNEES_DEMO_SQL)
        conn.commit()
        conn.close()
    
    def test_accueil_temps_reponse(self):
        """Teste que la page d'accueil répond rapidement."""
        import time
        
        client = Client()
        
        debut = time.time()
        response = client.get(reverse('blog:accueil'))
        duree = time.time() - debut
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duree, 2.0, "La page d'accueil devrait charger en moins de 2 secondes")
    
    def test_recherche_temps_reponse(self):
        """Teste que la recherche répond rapidement."""
        import time
        
        client = Client()
        
        debut = time.time()
        response = client.get(reverse('blog:recherche'), {'q': 'action'})
        duree = time.time() - debut
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duree, 1.0, "La recherche devrait répondre en moins de 1 seconde")


# =============================================================================
# TESTS DE SÉCURITÉ
# =============================================================================

class TestsSecurite(DjangoTestCase):
    """Tests de sécurité basiques."""
    
    def setUp(self):
        self.client = Client()
    
    def test_headers_securite(self):
        """Teste la présence de headers de sécurité."""
        response = self.client.get(reverse('blog:accueil'))
        
        # X-Frame-Options devrait être présent
        self.assertIn('X-Frame-Options', response)
    
    def test_csrf_protection(self):
        """Teste que la protection CSRF est active."""
        # Tenter une requête POST sans token CSRF
        response = self.client.post(reverse('blog:recherche'), {'q': 'test'})
        
        # Devrait être redirigé ou recevoir une erreur 403
        # (La recherche est GET only, donc 405)
        self.assertIn(response.status_code, [403, 405])
    
    def test_injection_sql_recherche(self):
        """Teste la résistance à l'injection SQL."""
        # Tentative d'injection SQL
        payload = "'; DROP TABLE contenus; --"
        
        response = self.client.get(
            reverse('blog:recherche'),
            {'q': payload}
        )
        
        # La requête devrait réussir sans erreur
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la table existe toujours
        from blog.db_operations import obtenir_tous_contenus
        contenus = obtenir_tous_contenus(limite=1)
        self.assertIsInstance(contenus, list)
