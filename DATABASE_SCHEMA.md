# Configuration du schéma Aura

Ce document explique comment configurer le schéma `aura` dans PostgreSQL pour l'application Aura.

## Vue d'ensemble

L'application Aura utilise un schéma PostgreSQL personnalisé nommé `aura` pour organiser les tables de la base de données. Cela permet une meilleure organisation et une séparation claire des données.

## Configuration

### 1. Variables d'environnement

Créez un fichier `.env` à la racine du projet avec la configuration suivante :

```bash
# Basic configuration
DEBUG=True
SECRET_KEY=your-secret-key-here

# PostgreSQL Database with aura schema
DATABASE_URL=postgres://aura_user:your-password@localhost:5432/aura_db?options=-csearch_path=aura

# Ou utilisez les variables séparées :
DB_NAME=aura_db
DB_USER=aura_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### 2. Création du schéma

#### Option A : Commande Django (Recommandée)

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # ou votre méthode d'activation

# Créer le schéma
python manage.py setup_aura_schema

# Appliquer les migrations
python manage.py makemigrations
python manage.py migrate
```

#### Option B : Script Python

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Exécuter le script de création
python setup/create_aura_schema.py

# Appliquer les migrations
python manage.py makemigrations
python manage.py migrate
```

#### Option C : SQL direct

Connectez-vous à PostgreSQL et exécutez :

```sql
-- Créer le schéma
CREATE SCHEMA IF NOT EXISTS aura;

-- Accorder les permissions
GRANT USAGE ON SCHEMA aura TO aura_user;
GRANT CREATE ON SCHEMA aura TO aura_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA aura TO aura_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA aura TO aura_user;

-- Définir le search_path
ALTER DATABASE aura_db SET search_path TO aura, public;
```

## Vérification

Pour vérifier que le schéma est correctement configuré :

```sql
-- Vérifier que le schéma existe
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'aura';

-- Vérifier le search_path
SHOW search_path;

-- Lister les tables dans le schéma aura
SELECT table_name FROM information_schema.tables WHERE table_schema = 'aura';
```

## Structure des schémas

- **`aura`** : Schéma principal contenant toutes les tables de l'application
- **`public`** : Schéma par défaut de PostgreSQL (utilisé pour les extensions)

## Dépannage

### Erreur de permissions

Si vous rencontrez des erreurs de permissions :

```sql
-- Accorder tous les privilèges sur le schéma
GRANT ALL PRIVILEGES ON SCHEMA aura TO aura_user;

-- Accorder les privilèges sur les futures tables
ALTER DEFAULT PRIVILEGES IN SCHEMA aura GRANT ALL ON TABLES TO aura_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA aura GRANT ALL ON SEQUENCES TO aura_user;
```

### Tables dans le mauvais schéma

Si les tables sont créées dans le schéma `public` au lieu de `aura` :

1. Vérifiez que `search_path` est correctement configuré
2. Redémarrez la connexion à la base de données
3. Vérifiez la configuration Django dans `settings/base.py`

### Migration des données existantes

Si vous avez des données existantes dans le schéma `public` :

```sql
-- Déplacer les tables vers le schéma aura
ALTER TABLE public.table_name SET SCHEMA aura;
```

## Notes importantes

- Le schéma `aura` est configuré comme prioritaire dans le `search_path`
- Toutes les nouvelles tables Django seront créées dans le schéma `aura`
- Les migrations Django fonctionneront normalement avec cette configuration
- Assurez-vous que l'utilisateur de base de données a les permissions appropriées
