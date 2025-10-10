# Guide de Migration PostgreSQL pour Aura

Ce guide vous accompagne dans la configuration de PostgreSQL et la migration de vos données vers la nouvelle architecture avec le schéma `aura`.

## 📋 Prérequis

- PostgreSQL installé et configuré
- Python 3.13+ avec `uv` ou `pip`
- Accès administrateur à PostgreSQL
- Fichier `.env` configuré

## 🚀 Étapes de Migration

### 1. Configuration de l'Environnement

#### 1.1 Créer le fichier `.env`
```bash
# Le fichier .env a déjà été créé depuis env.example
# Modifiez-le avec vos vraies informations de base de données
```

#### 1.2 Modifier le fichier `.env`
Éditez le fichier `.env` avec vos informations de base de données :

```bash
# Basic configuration
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database Configuration
POSTGRES_DB=aura_db
POSTGRES_USER=aura_user
POSTGRES_PASSWORD=your-secure-password-here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 2. Configuration PostgreSQL

#### 2.1 Exécuter le script de configuration
```bash
# Rendre le script exécutable
chmod +x setup_postgresql.sh

# Exécuter le script de configuration
./setup_postgresql.sh
```

Ce script va :
- Vérifier que PostgreSQL est installé et démarré
- Créer la base de données `aura_db`
- Créer l'utilisateur `aura_user`
- Créer le schéma `aura`
- Configurer les permissions
- Définir le `search_path`

#### 2.2 Vérification manuelle (optionnel)
```bash
# Se connecter à PostgreSQL
psql -h localhost -p 5432 -U aura_user -d aura_db

# Vérifier le schéma
\dn

# Vérifier le search_path
SHOW search_path;

# Quitter
\q
```

### 3. Configuration Django

#### 3.1 Installer les dépendances
```bash
# Avec uv (recommandé)
uv sync

# Ou avec pip
pip install -r requirements.txt
```

#### 3.2 Créer le schéma avec Django
```bash
# Créer le schéma aura
python manage.py setup_aura_schema

# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

### 4. Migration des Données

#### 4.1 Exporter les données existantes (si nécessaire)

Si vous avez des données dans une autre base de données, exportez-les d'abord :

```bash
# Exporter vers JSON
python export_data.py --output data_export.json
```

#### 4.2 Migrer les données vers PostgreSQL

**Option A : Avec la commande Django (recommandée)**
```bash
# Migration normale
python manage.py migrate_from_json --file data_export.json

# Test en mode dry-run
python manage.py migrate_from_json --file data_export.json --dry-run

# Migration avec suppression des données existantes
python manage.py migrate_from_json --file data_export.json --clear
```

**Option B : Avec le script Python**
```bash
# Migration avec le script Python
python migrate_data.py --json-file data_export.json
```

### 5. Vérification et Finalisation

#### 5.1 Créer un superutilisateur
```bash
python manage.py createsuperuser
```

#### 5.2 Tester l'application
```bash
python manage.py runserver
```

Visitez `http://localhost:8000` pour vérifier que tout fonctionne.

#### 5.3 Vérifier les données dans PostgreSQL
```bash
# Se connecter à la base de données
psql -h localhost -p 5432 -U aura_user -d aura_db

# Lister les tables dans le schéma aura
\dt aura.*

# Vérifier quelques données
SELECT COUNT(*) FROM aura.core_user;
SELECT COUNT(*) FROM aura.artworks_artwork;

# Quitter
\q
```

## 🔧 Dépannage

### Problèmes Courants

#### 1. Erreur de connexion PostgreSQL
```bash
# Vérifier que PostgreSQL est démarré
pg_isready

# Démarrer PostgreSQL (macOS avec Homebrew)
brew services start postgresql

# Démarrer PostgreSQL (Linux)
sudo systemctl start postgresql
```

#### 2. Erreur de permissions
```sql
-- Se connecter en tant que superutilisateur PostgreSQL
sudo -u postgres psql

-- Accorder les permissions
GRANT ALL PRIVILEGES ON DATABASE aura_db TO aura_user;
GRANT ALL PRIVILEGES ON SCHEMA aura TO aura_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA aura TO aura_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA aura TO aura_user;

-- Définir les permissions par défaut
ALTER DEFAULT PRIVILEGES IN SCHEMA aura GRANT ALL ON TABLES TO aura_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA aura GRANT ALL ON SEQUENCES TO aura_user;
```

#### 3. Tables créées dans le mauvais schéma
```sql
-- Vérifier le search_path
SHOW search_path;

-- Si nécessaire, redéfinir le search_path
ALTER DATABASE aura_db SET search_path TO aura, public;

-- Redémarrer la connexion Django
```

#### 4. Erreur de migration des données
```bash
# Vérifier les logs
tail -f migration.log

# Tester avec un petit échantillon de données
python manage.py migrate_from_json --file data_export.json --dry-run
```

### Commandes Utiles

#### Vérification de l'état
```bash
# Vérifier la configuration Django
python manage.py check

# Vérifier les migrations
python manage.py showmigrations

# Vérifier la base de données
python manage.py dbshell
```

#### Nettoyage (si nécessaire)
```bash
# Supprimer toutes les migrations (ATTENTION!)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recréer les migrations
python manage.py makemigrations
python manage.py migrate
```

## 📊 Structure de la Base de Données

### Schéma `aura`
- `core_user` : Utilisateurs
- `core_userprofile` : Profils utilisateurs
- `artworks_artist` : Artistes
- `artworks_artwork` : Œuvres d'art
- `artworks_collection` : Collections
- `artworks_exhibition` : Expositions
- `artworks_arttype` : Types d'art
- `artworks_support` : Supports
- `artworks_technique` : Techniques
- `contacts_contact` : Contacts
- `notes_note` : Notes

### Schéma `public`
- Extensions PostgreSQL
- Tables système

## 🔒 Sécurité

### Bonnes Pratiques
1. **Mots de passe forts** : Utilisez des mots de passe complexes pour la base de données
2. **Permissions minimales** : L'utilisateur `aura_user` n'a que les permissions nécessaires
3. **Schéma isolé** : Les données sont dans le schéma `aura`, séparées du schéma `public`
4. **Variables d'environnement** : Les informations sensibles sont dans `.env`

### Configuration Production
```bash
# Dans .env pour la production
DEBUG=False
SECRET_KEY=your-very-secure-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
POSTGRES_PASSWORD=very-secure-database-password
```

## 📝 Logs et Monitoring

### Fichiers de Log
- `migration.log` : Logs de migration des données
- `export.log` : Logs d'export des données
- Logs Django : Configurés dans les settings

### Monitoring
```bash
# Vérifier l'état de PostgreSQL
pg_isready

# Vérifier les connexions actives
psql -c "SELECT * FROM pg_stat_activity;"

# Vérifier l'espace disque
df -h
```

## 🎯 Prochaines Étapes

1. **Sauvegarde** : Configurez des sauvegardes automatiques
2. **Monitoring** : Mettez en place un monitoring de la base de données
3. **Optimisation** : Analysez les performances et optimisez si nécessaire
4. **Documentation** : Documentez votre configuration spécifique

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs d'erreur
2. Consultez la documentation PostgreSQL
3. Vérifiez la configuration Django
4. Testez avec des données d'exemple

---

**Note** : Ce guide suppose une installation PostgreSQL standard. Adaptez les commandes selon votre configuration spécifique.


