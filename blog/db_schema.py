"""
Schéma de base de données pour le Blog Académique du Professeur.

Ce module contient les requêtes SQL pour créer et gérer
la structure de la base de données SQLite.

IMPORTANT: Ce projet n'utilise PAS l'ORM Django.
Toutes les opérations sont effectuées en SQL brut.
"""

# =============================================================================
# SCHÉMA SQL - CRÉATION DES TABLES
# =============================================================================

SCHEMA_SQL = """
-- ============================================================================
-- TABLE: categories
-- Description: Catégories/thèmes pour articles et livres
-- ============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icone VARCHAR(50),
    ordre INTEGER DEFAULT 0,
    est_active INTEGER DEFAULT 1,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: articles
-- Description: Articles et publications du blog académique
-- ============================================================================
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    contenu TEXT,
    extrait VARCHAR(500),
    type_article VARCHAR(20) NOT NULL DEFAULT 'article' CHECK(type_article IN ('article', 'publication', 'actualite', 'recherche')),
    image_url TEXT,
    banniere_url TEXT,
    auteur VARCHAR(100) DEFAULT 'Professeur',
    temps_lecture INTEGER,
    est_vedette INTEGER DEFAULT 0,
    est_populaire INTEGER DEFAULT 0,
    est_nouveau INTEGER DEFAULT 0,
    est_publie INTEGER DEFAULT 1,
    ordre_affichage INTEGER DEFAULT 0,
    meta_keywords TEXT,
    meta_description TEXT,
    date_publication DATE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: article_categories (relation many-to-many)
-- Description: Associe les articles aux catégories
-- ============================================================================
CREATE TABLE IF NOT EXISTS article_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    categorie_id INTEGER NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (categorie_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE(article_id, categorie_id)
);

-- ============================================================================
-- TABLE: livres
-- Description: Livres et ouvrages du professeur (gratuits ou payants)
-- ============================================================================
CREATE TABLE IF NOT EXISTS livres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    extrait TEXT,
    auteur VARCHAR(100) DEFAULT 'Professeur',
    co_auteurs TEXT,
    isbn VARCHAR(20),
    editeur VARCHAR(100),
    annee_publication INTEGER,
    nombre_pages INTEGER,
    langue VARCHAR(50) DEFAULT 'Français',
    image_couverture TEXT,
    fichier_pdf TEXT,
    fichier_preview TEXT,
    prix DECIMAL(10, 2) DEFAULT 0.00,
    devise VARCHAR(10) DEFAULT 'CFA',
    est_gratuit INTEGER DEFAULT 1,
    est_vedette INTEGER DEFAULT 0,
    est_nouveau INTEGER DEFAULT 0,
    est_publie INTEGER DEFAULT 1,
    ordre_affichage INTEGER DEFAULT 0,
    nombre_telechargements INTEGER DEFAULT 0,
    meta_keywords TEXT,
    meta_description TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: livre_categories (relation many-to-many)
-- Description: Associe les livres aux catégories
-- ============================================================================
CREATE TABLE IF NOT EXISTS livre_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    livre_id INTEGER NOT NULL,
    categorie_id INTEGER NOT NULL,
    FOREIGN KEY (livre_id) REFERENCES livres(id) ON DELETE CASCADE,
    FOREIGN KEY (categorie_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE(livre_id, categorie_id)
);

-- ============================================================================
-- TABLE: achats
-- Description: Enregistrement des achats de livres payants
-- ============================================================================
CREATE TABLE IF NOT EXISTS achats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    livre_id INTEGER NOT NULL,
    nom_client VARCHAR(100) NOT NULL,
    email_client VARCHAR(100) NOT NULL,
    telephone_client VARCHAR(20),
    montant DECIMAL(10, 2) NOT NULL,
    devise VARCHAR(10) DEFAULT 'EUR',
    methode_paiement VARCHAR(50),
    reference_transaction VARCHAR(100),
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK(statut IN ('en_attente', 'paye', 'echoue', 'rembourse')),
    token_telechargement VARCHAR(100) UNIQUE,
    nombre_telechargements INTEGER DEFAULT 0,
    max_telechargements INTEGER DEFAULT 3,
    expire_le TIMESTAMP,
    notes TEXT,
    date_achat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (livre_id) REFERENCES livres(id) ON DELETE CASCADE
);

-- ============================================================================
-- TABLE: telechargements
-- Description: Historique des téléchargements de livres
-- ============================================================================
CREATE TABLE IF NOT EXISTS telechargements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    livre_id INTEGER NOT NULL,
    achat_id INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    date_telechargement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (livre_id) REFERENCES livres(id) ON DELETE CASCADE,
    FOREIGN KEY (achat_id) REFERENCES achats(id) ON DELETE SET NULL
);

-- ============================================================================
-- TABLE: liens_footer
-- Description: Liens affichés dans le pied de page
-- ============================================================================
CREATE TABLE IF NOT EXISTS liens_footer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre VARCHAR(100) NOT NULL,
    url VARCHAR(255) NOT NULL,
    groupe VARCHAR(50) NOT NULL,
    ordre INTEGER DEFAULT 0,
    est_actif INTEGER DEFAULT 1,
    ouvre_nouvel_onglet INTEGER DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: configuration_site
-- Description: Paramètres configurables du site
-- ============================================================================
CREATE TABLE IF NOT EXISTS configuration_site (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cle VARCHAR(100) NOT NULL UNIQUE,
    valeur TEXT,
    type_valeur VARCHAR(20) DEFAULT 'texte',
    description TEXT,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: reseaux_sociaux
-- Description: Liens vers les réseaux sociaux et profils académiques
-- ============================================================================
CREATE TABLE IF NOT EXISTS reseaux_sociaux (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(50) NOT NULL,
    url VARCHAR(255) NOT NULL,
    icone VARCHAR(50) NOT NULL,
    ordre INTEGER DEFAULT 0,
    est_actif INTEGER DEFAULT 1
);

-- ============================================================================
-- TABLE: statistiques_vues
-- Description: Suivi des vues pour le classement
-- ============================================================================
CREATE TABLE IF NOT EXISTS statistiques_vues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER,
    livre_id INTEGER,
    nombre_vues INTEGER DEFAULT 0,
    date_vue DATE NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (livre_id) REFERENCES livres(id) ON DELETE CASCADE,
    UNIQUE(article_id, date_vue),
    UNIQUE(livre_id, date_vue)
);

-- ============================================================================
-- TABLE: messages_contact
-- Description: Messages reçus via le formulaire de contact
-- ============================================================================
CREATE TABLE IF NOT EXISTS messages_contact (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    sujet VARCHAR(200),
    message TEXT NOT NULL,
    est_lu INTEGER DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: abonnes_newsletter
-- Description: Inscriptions à la newsletter
-- ============================================================================
CREATE TABLE IF NOT EXISTS abonnes_newsletter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) NOT NULL UNIQUE,
    nom VARCHAR(100),
    est_actif INTEGER DEFAULT 1,
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEX pour optimiser les requêtes
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_articles_type ON articles(type_article);
CREATE INDEX IF NOT EXISTS idx_articles_vedette ON articles(est_vedette);
CREATE INDEX IF NOT EXISTS idx_articles_populaire ON articles(est_populaire);
CREATE INDEX IF NOT EXISTS idx_articles_publie ON articles(est_publie);
CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_livres_slug ON livres(slug);
CREATE INDEX IF NOT EXISTS idx_livres_gratuit ON livres(est_gratuit);
CREATE INDEX IF NOT EXISTS idx_livres_vedette ON livres(est_vedette);
CREATE INDEX IF NOT EXISTS idx_achats_statut ON achats(statut);
CREATE INDEX IF NOT EXISTS idx_achats_token ON achats(token_telechargement);
CREATE INDEX IF NOT EXISTS idx_achats_email ON achats(email_client);
CREATE INDEX IF NOT EXISTS idx_messages_lu ON messages_contact(est_lu);

-- ============================================================================
-- TRIGGERS pour mise à jour automatique des dates
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS maj_articles_modification
AFTER UPDATE ON articles
BEGIN
    UPDATE articles SET date_modification = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS maj_categories_modification
AFTER UPDATE ON categories
BEGIN
    UPDATE categories SET date_modification = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS maj_livres_modification
AFTER UPDATE ON livres
BEGIN
    UPDATE livres SET date_modification = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
"""

# =============================================================================
# DONNÉES INITIALES
# =============================================================================

DONNEES_INITIALES_SQL = """
-- Catégories académiques par défaut
INSERT OR IGNORE INTO categories (nom, slug, description, icone, ordre) VALUES
    ('Sciences', 'sciences', 'Articles et recherches scientifiques', 'ti-atom', 1),
    ('Recherche', 'recherche', 'Publications et travaux de recherche', 'ti-microscope', 2),
    ('Éducation', 'education', 'Pédagogie et enseignement', 'ti-school', 3),
    ('Philosophie', 'philosophie', 'Réflexions philosophiques', 'ti-brain', 4),
    ('Histoire', 'histoire', 'Études historiques', 'ti-history', 5),
    ('Littérature', 'litterature', 'Analyses littéraires', 'ti-book', 6),
    ('Économie', 'economie', 'Sciences économiques', 'ti-chart-line', 7),
    ('Société', 'societe', 'Questions sociales et sociétales', 'ti-users', 8),
    ('Actualités', 'actualites', 'Actualités académiques', 'ti-news', 9),
    ('Conférences', 'conferences', 'Comptes-rendus de conférences', 'ti-microphone', 10);

-- Configuration du site par défaut
INSERT OR IGNORE INTO configuration_site (cle, valeur, type_valeur, description) VALUES
    ('nom_site', 'Mr Talnan', 'texte', 'Nom affiché dans le header'),
    ('titre_site', 'Blog Académique', 'texte', 'Titre du site'),
    ('nom_professeur', 'Mr Talnan', 'texte', 'Nom complet du professeur'),
    ('titre_academique', 'Professeur des Universités', 'texte', 'Titre académique'),
    ('specialite', 'Sciences de l''Éducation', 'texte', 'Spécialité académique'),
    ('universite', 'Université de Paris', 'texte', 'Affiliation universitaire'),
    ('email_contact', 'contact@prof-dupont.com', 'email', 'Email de contact'),
    ('telephone', '+33 1 23 45 67 89', 'texte', 'Numéro de téléphone'),
    ('adresse', 'Université de Paris, 75005 Paris', 'texte', 'Adresse professionnelle'),
    ('mots_cles', 'professeur, université, recherche, éducation, publications, livres', 'texte', 'Mots-clés pour le SEO'),
    ('a_propos', 'Professeur des Universités depuis plus de 20 ans, je partage sur ce blog mes recherches, publications et réflexions sur les Sciences de l''Éducation. Mon objectif est de rendre le savoir accessible à tous.', 'texte', 'Texte de présentation'),
    ('photo_profil', '', 'texte', 'URL de la photo de profil'),
    ('cv_url', '', 'texte', 'URL du CV en ligne');

-- Réseaux sociaux et profils académiques par défaut
INSERT OR IGNORE INTO reseaux_sociaux (nom, url, icone, ordre) VALUES
    ('ResearchGate', 'https://researchgate.net/', 'ti-flask', 1),
    ('Google Scholar', 'https://scholar.google.com/', 'ti-school', 2),
    ('LinkedIn', 'https://linkedin.com/', 'ti-brand-linkedin', 3),
    ('ORCID', 'https://orcid.org/', 'ti-id', 4),
    ('Twitter/X', 'https://twitter.com/', 'ti-brand-twitter', 5);

-- Liens footer par défaut
INSERT OR IGNORE INTO liens_footer (titre, url, groupe, ordre) VALUES
    -- Groupe Publications
    ('Articles', '/articles/', 'publications', 1),
    ('Recherches', '/recherches/', 'publications', 2),
    ('Actualités', '/categorie/actualites/', 'publications', 3),
    ('Conférences', '/categorie/conferences/', 'publications', 4),
    -- Groupe Livres
    ('Tous les livres', '/livres/', 'livres', 1),
    ('Livres gratuits', '/livres/?gratuit=1', 'livres', 2),
    ('Nouveautés', '/livres/?nouveau=1', 'livres', 3),
    -- Groupe Informations
    ('À propos', '/a-propos/', 'informations', 1),
    ('CV & Parcours', '/cv/', 'informations', 2),
    ('Contact', '/contact/', 'informations', 3),
    ('Mentions Légales', '/mentions-legales/', 'informations', 4);
"""

# =============================================================================
# DONNÉES DE DÉMONSTRATION
# =============================================================================

DONNEES_DEMO_SQL = """
-- Articles de démonstration
INSERT OR IGNORE INTO articles (
    titre, slug, contenu, extrait,
    type_article, image_url, banniere_url, auteur,
    temps_lecture, est_vedette, est_populaire, est_nouveau, ordre_affichage
) VALUES
    (
        'L''Avenir de l''Éducation à l''Ère Numérique',
        'avenir-education-ere-numerique',
        'L''éducation traverse une période de transformation sans précédent. Les technologies numériques bouleversent nos méthodes d''enseignement traditionnelles et ouvrent de nouvelles perspectives pédagogiques.

## Les Défis Actuels

L''intégration du numérique dans l''éducation soulève de nombreuses questions :

1. **L''accessibilité** - Comment garantir un accès équitable aux outils numériques ?
2. **La formation des enseignants** - Quelles compétences développer ?
3. **L''attention des élèves** - Comment maintenir l''engagement ?

## Les Opportunités

Malgré ces défis, les opportunités sont immenses :

- Personnalisation des apprentissages
- Accès à des ressources mondiales
- Collaboration internationale
- Nouvelles formes d''évaluation

## Conclusion

L''avenir de l''éducation sera hybride, combinant le meilleur du présentiel et du numérique.',
        'Une réflexion approfondie sur les transformations de l''éducation face aux technologies numériques.',
        'article',
        'https://images.unsplash.com/photo-1509062522246-3755977927d7?w=800',
        'https://images.unsplash.com/photo-1509062522246-3755977927d7?w=1600',
        'Mr Talnan',
        12, 1, 1, 0, 1
    ),
    (
        'Méthodologie de la Recherche Qualitative',
        'methodologie-recherche-qualitative',
        'La recherche qualitative est une approche essentielle dans les sciences humaines et sociales. Cet article présente les fondamentaux méthodologiques pour mener une recherche rigoureuse.

## Principes Fondamentaux

La recherche qualitative se distingue par :

- Une approche compréhensive
- L''importance du contexte
- La flexibilité méthodologique
- L''interprétation des significations

## Techniques de Collecte

Plusieurs techniques peuvent être mobilisées :

1. **L''entretien semi-directif**
2. **L''observation participante**
3. **L''analyse documentaire**
4. **Les focus groups**

## Analyse des Données

L''analyse thématique reste la méthode la plus utilisée pour interpréter les données qualitatives.',
        'Guide méthodologique pour mener une recherche qualitative rigoureuse en sciences humaines.',
        'recherche',
        'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800',
        'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1600',
        'Mr Talnan',
        15, 1, 1, 0, 2
    ),
    (
        'La Pensée Critique dans l''Enseignement Supérieur',
        'pensee-critique-enseignement-superieur',
        'Développer la pensée critique chez les étudiants est un objectif fondamental de l''enseignement supérieur. Comment y parvenir efficacement ?

## Qu''est-ce que la Pensée Critique ?

La pensée critique implique :

- L''analyse objective des informations
- L''évaluation des sources
- La construction d''arguments logiques
- La remise en question des présupposés

## Stratégies Pédagogiques

Pour développer la pensée critique :

1. Poser des questions ouvertes
2. Encourager le débat
3. Proposer des études de cas
4. Demander des justifications

## Évaluation

L''évaluation de la pensée critique nécessite des dispositifs adaptés : portfolios, dissertations argumentées, présentations orales.',
        'Comment développer efficacement la pensée critique chez les étudiants universitaires.',
        'article',
        'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800',
        'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600',
        'Mr Talnan',
        10, 0, 1, 1, 3
    ),
    (
        'Publication : Les Nouvelles Approches Pédagogiques',
        'publication-nouvelles-approches-pedagogiques',
        'Notre dernière publication dans la Revue Française de Pédagogie explore les innovations pédagogiques dans l''enseignement supérieur.

## Résumé

Cette étude analyse les pratiques innovantes de 50 enseignants-chercheurs dans 10 universités françaises.

## Principaux Résultats

- 78% utilisent des méthodes actives
- 65% intègrent le numérique
- 45% pratiquent la classe inversée

## Implications

Ces résultats suggèrent une transformation progressive mais réelle des pratiques pédagogiques universitaires.',
        'Dernière publication académique sur les innovations pédagogiques dans l''enseignement supérieur.',
        'publication',
        'https://images.unsplash.com/photo-1456324504439-367cee3b3c32?w=800',
        'https://images.unsplash.com/photo-1456324504439-367cee3b3c32?w=1600',
        'Mr Talnan',
        8, 0, 1, 1, 4
    ),
    (
        'Conférence Internationale sur l''Éducation 2024',
        'conference-internationale-education-2024',
        'Compte-rendu de ma participation à la Conférence Internationale sur l''Éducation qui s''est tenue à Genève.

## Thèmes Abordés

La conférence a exploré plusieurs thématiques :

- L''éducation inclusive
- Les compétences du 21e siècle
- L''intelligence artificielle en éducation
- Le développement durable

## Ma Contribution

J''ai présenté mes travaux sur l''évaluation des compétences transversales, suscitant de nombreux échanges enrichissants.

## Perspectives

Cette conférence confirme l''importance croissante des approches interdisciplinaires en éducation.',
        'Retour sur la Conférence Internationale sur l''Éducation et les tendances actuelles.',
        'actualite',
        'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800',
        'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1600',
        'Mr Talnan',
        6, 0, 0, 1, 5
    ),
    (
        'L''Importance de la Lecture dans la Formation',
        'importance-lecture-formation',
        'La lecture reste un pilier fondamental de toute formation universitaire. Pourquoi et comment encourager cette pratique ?

## Pourquoi Lire ?

La lecture développe :

- Le vocabulaire et l''expression
- La capacité d''analyse
- L''esprit critique
- La culture générale

## Comment Lire Efficacement ?

1. Prendre des notes
2. Surligner les passages clés
3. Faire des résumés
4. Discuter des lectures

## Recommandations

Je propose chaque semestre une liste de lectures essentielles à mes étudiants, couvrant les classiques et les publications récentes.',
        'Réflexion sur le rôle central de la lecture dans la formation universitaire.',
        'article',
        'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=800',
        'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1600',
        'Mr Talnan',
        7, 0, 1, 0, 6
    );

-- Livres de démonstration
INSERT OR IGNORE INTO livres (
    titre, slug, description, extrait, auteur,
    editeur, annee_publication, nombre_pages, langue,
    image_couverture, prix, devise, est_gratuit,
    est_vedette, est_nouveau, ordre_affichage
) VALUES
    (
        'Introduction aux Sciences de l''Éducation',
        'introduction-sciences-education',
        'Un ouvrage fondamental pour comprendre les grandes théories et concepts des Sciences de l''Éducation. Ce livre est destiné aux étudiants de licence et master ainsi qu''aux professionnels de l''éducation.

**Au programme :**
- Histoire des Sciences de l''Éducation
- Les grands courants pédagogiques
- Méthodologie de la recherche
- Applications pratiques',
        'Chapitre 1 : Qu''est-ce que les Sciences de l''Éducation ?

Les Sciences de l''Éducation constituent un champ disciplinaire relativement récent dans l''université française...',
        'Mr Talnan',
        'Éditions Universitaires',
        2023,
        350,
        'Français',
        'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400',
        0.00,
        'CFA',
        1,
        1, 0, 1
    ),
    (
        'Pédagogie et Innovation : Guide Pratique',
        'pedagogie-innovation-guide-pratique',
        'Ce guide pratique propose des outils concrets pour innover dans sa pratique pédagogique. Basé sur 20 ans d''expérience et de recherche.

**Contenu :**
- 50 fiches pratiques
- Études de cas
- Grilles d''évaluation
- Ressources numériques',
        'Introduction : Pourquoi innover ?

L''innovation pédagogique n''est pas une fin en soi. Elle répond à un besoin d''adaptation aux évolutions de la société et des publics étudiants...',
        'Mr Talnan',
        'Éditions Pédagogiques',
        2024,
        280,
        'Français',
        'https://images.unsplash.com/photo-1589998059171-988d887df646?w=400',
        16300,
        'CFA',
        0,
        1, 1, 2
    ),
    (
        'L''Évaluation des Compétences',
        'evaluation-competences',
        'Un ouvrage de référence sur l''évaluation des compétences dans l''enseignement supérieur. Théories, méthodes et outils pratiques.

**Points forts :**
- Cadre théorique solide
- Exemples concrets
- Outils téléchargeables
- Bibliographie commentée',
        'Préface

L''évaluation des compétences représente aujourd''hui un enjeu majeur pour les systèmes éducatifs du monde entier...',
        'Mr Talnan',
        'Presses Universitaires',
        2022,
        420,
        'Français',
        'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400',
        22600,
        'CFA',
        0,
        0, 0, 3
    ),
    (
        'Actes du Colloque : Éducation et Numérique',
        'actes-colloque-education-numerique',
        'Les actes du colloque international sur l''Éducation et le Numérique organisé à l''Université de Paris. Contributions de chercheurs internationaux.

**15 communications scientifiques** sur les thèmes :
- MOOC et e-learning
- Intelligence artificielle
- Réalité virtuelle
- Accessibilité numérique',
        'Introduction

Ce colloque a réuni 150 chercheurs de 25 pays pour débattre des enjeux du numérique en éducation...',
        'Mr Talnan (dir.)',
        'Éditions Numériques',
        2023,
        250,
        'Français',
        'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400',
        0.00,
        'EUR',
        1,
        0, 0, 4
    ),
    (
        'Réussir sa Thèse en Sciences Humaines',
        'reussir-these-sciences-humaines',
        'Le guide indispensable pour les doctorants en sciences humaines et sociales. De la conception à la soutenance.

**Chapitres :**
1. Choisir son sujet
2. Construire sa problématique
3. Méthodologie
4. Rédaction
5. Soutenance',
        'Avant-propos

Réussir une thèse est un défi intellectuel et personnel. Ce guide vous accompagnera tout au long de ce parcours exigeant...',
        'Mr Talnan',
        'Éditions Universitaires',
        2021,
        180,
        'Français',
        'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400',
        13000,
        'CFA',
        0,
        0, 0, 5
    );

-- Associations articles-catégories
INSERT OR IGNORE INTO article_categories (article_id, categorie_id)
SELECT a.id, c.id FROM articles a, categories c
WHERE a.slug = 'avenir-education-ere-numerique' AND c.slug IN ('education', 'actualites');

INSERT OR IGNORE INTO article_categories (article_id, categorie_id)
SELECT a.id, c.id FROM articles a, categories c
WHERE a.slug = 'methodologie-recherche-qualitative' AND c.slug IN ('recherche', 'education');

INSERT OR IGNORE INTO article_categories (article_id, categorie_id)
SELECT a.id, c.id FROM articles a, categories c
WHERE a.slug = 'pensee-critique-enseignement-superieur' AND c.slug IN ('education', 'philosophie');

INSERT OR IGNORE INTO article_categories (article_id, categorie_id)
SELECT a.id, c.id FROM articles a, categories c
WHERE a.slug = 'publication-nouvelles-approches-pedagogiques' AND c.slug IN ('recherche', 'education');

INSERT OR IGNORE INTO article_categories (article_id, categorie_id)
SELECT a.id, c.id FROM articles a, categories c
WHERE a.slug = 'conference-internationale-education-2024' AND c.slug IN ('conferences', 'actualites');

INSERT OR IGNORE INTO article_categories (article_id, categorie_id)
SELECT a.id, c.id FROM articles a, categories c
WHERE a.slug = 'importance-lecture-formation' AND c.slug IN ('education', 'litterature');

-- Associations livres-catégories
INSERT OR IGNORE INTO livre_categories (livre_id, categorie_id)
SELECT l.id, c.id FROM livres l, categories c
WHERE l.slug = 'introduction-sciences-education' AND c.slug IN ('education', 'sciences');

INSERT OR IGNORE INTO livre_categories (livre_id, categorie_id)
SELECT l.id, c.id FROM livres l, categories c
WHERE l.slug = 'pedagogie-innovation-guide-pratique' AND c.slug IN ('education');

INSERT OR IGNORE INTO livre_categories (livre_id, categorie_id)
SELECT l.id, c.id FROM livres l, categories c
WHERE l.slug = 'evaluation-competences' AND c.slug IN ('education', 'recherche');

INSERT OR IGNORE INTO livre_categories (livre_id, categorie_id)
SELECT l.id, c.id FROM livres l, categories c
WHERE l.slug = 'actes-colloque-education-numerique' AND c.slug IN ('conferences', 'education');

INSERT OR IGNORE INTO livre_categories (livre_id, categorie_id)
SELECT l.id, c.id FROM livres l, categories c
WHERE l.slug = 'reussir-these-sciences-humaines' AND c.slug IN ('education', 'recherche');
"""
