# Aura Art - Guide de Déploiement Docker

Ce guide explique comment déployer l'application Aura Art avec Docker et Docker Compose.

## Table des Matières

1. [Prérequis](#prérequis)
2. [Architecture](#architecture)
3. [Démarrage Rapide](#démarrage-rapide)
4. [Configuration](#configuration)
5. [Déploiement Production](#déploiement-production)
6. [Maintenance](#maintenance)
7. [Dépannage](#dépannage)

---

## Prérequis

### Logiciels Requis

- **Docker** 24.0+ : [Installation](https://docs.docker.com/engine/install/)
- **Docker Compose** 2.0+ : [Installation](https://docs.docker.com/compose/install/)
- **Git** : Pour cloner le repository
- **Make** (optionnel) : Pour utiliser le Makefile

### Ressources Serveur Recommandées

| Environnement | CPU | RAM | Disque |
|---------------|-----|-----|--------|
| Développement | 2 cores | 4 GB | 20 GB |
| Staging | 2 cores | 8 GB | 50 GB |
| Production | 4 cores | 16 GB | 100 GB |

---

## Architecture

### Conteneurs

L'application est composée de 4 conteneurs principaux :

```
┌─────────────────────────────────────────┐
│            Nginx (Port 80/443)           │
│     Reverse Proxy + SSL + Static        │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        Django/Gunicorn (Port 8000)      │
│           Application Web + API          │
└──────┬──────────────────────┬───────────┘
       │                      │
┌──────▼────────┐    ┌───────▼────────┐
│  PostgreSQL   │    │  Redis (Cache) │
│  (Port 5432)  │    │  (Port 6379)   │
└───────────────┘    └────────────────┘
```

### Volumes Docker

- `postgres_data` : Données PostgreSQL persistantes
- `redis_data` : Données Redis persistantes
- `static_volume` : Fichiers statiques Django
- `media_volume` : Fichiers média uploadés

---

## Démarrage Rapide

### 1. Cloner le Repository

```bash
git clone <repository-url>
cd aura-app
```

### 2. Configuration Environnement de Développement

```bash
# Copier le fichier d'environnement exemple
cp .env.production.example .env

# Éditer les variables (utiliser les valeurs par défaut pour dev)
nano .env
```

**Variables minimales pour le développement :**

```env
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
DATABASE_URL=postgresql://aura_user:changeme@db:5432/aura_db
```

### 3. Démarrer les Services

```bash
# Option 1 : Avec Make
make docker-build
make docker-up

# Option 2 : Directement avec Docker Compose
docker compose build
docker compose up -d
```

### 4. Initialiser la Base de Données

```bash
# Créer les tables
docker compose exec web python manage.py migrate

# Créer un superutilisateur
docker compose exec web python manage.py createsuperuser

# Collecter les fichiers statiques
docker compose exec web python manage.py collectstatic --noinput
```

### 5. Accéder à l'Application

- **Application** : http://localhost
- **Admin** : http://localhost/admin/
- **API** : http://localhost/api/
- **Health Check** : http://localhost/health/

---

## Configuration

### Variables d'Environnement

Toutes les variables sont définies dans `.env`. Voir [.env.production.example](.env.production.example) pour la liste complète.

#### Variables Critiques

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète Django (50+ caractères) | `django-insecure-...` |
| `DEBUG` | Mode debug (False en production) | `False` |
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://user:pass@db/dbname` |
| `ALLOWED_HOSTS` | Domaines autorisés | `aura-art.org,www.aura-art.org` |
| `CSRF_TRUSTED_ORIGINS` | Origines CSRF de confiance | `https://aura-art.org` |

#### Variables AWS S3 (Optionnel)

Pour utiliser S3 pour le stockage des médias :

```env
AWS_STORAGE_BUCKET_NAME=my-bucket
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_S3_REGION_NAME=us-east-1
```

### Fichiers de Configuration

- **[docker-compose.yml](docker-compose.yml)** : Configuration de base pour dev/staging
- **[docker-compose.prod.yml](docker-compose.prod.yml)** : Overrides pour production
- **[Dockerfile](Dockerfile)** : Image Django/Gunicorn
- **[Dockerfile.nginx](Dockerfile.nginx)** : Image Nginx
- **[nginx.conf](nginx.conf)** : Configuration Nginx
- **[entrypoint.sh](entrypoint.sh)** : Script d'initialisation Django

---

## Déploiement Production

### 1. Préparer le Serveur

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Installer Docker Compose
sudo apt install docker-compose-plugin -y

# Configurer le firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. Créer les Répertoires

```bash
# Répertoires de données
sudo mkdir -p /var/lib/aura/{postgres,redis}
sudo mkdir -p /var/www/aura/{static,media}

# Permissions
sudo chown -R $USER:$USER /var/lib/aura /var/www/aura
```

### 3. Obtenir les Certificats SSL

```bash
# Installer Certbot
sudo apt install certbot -y

# Obtenir les certificats (méthode standalone)
sudo systemctl stop nginx  # Si nginx est déjà installé
sudo certbot certonly --standalone -d aura-art.org -d www.aura-art.org

# Les certificats seront dans :
# /etc/letsencrypt/live/aura-art.org/
```

### 4. Configurer les Variables d'Environnement

```bash
# Copier et éditer .env
cp .env.production.example .env
nano .env
```

**Générer un SECRET_KEY sécurisé :**

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

**Variables Production Minimales :**

```env
SECRET_KEY=<généré-ci-dessus>
DEBUG=False
ALLOWED_HOSTS=aura-art.org,www.aura-art.org
CSRF_TRUSTED_ORIGINS=https://aura-art.org,https://www.aura-art.org
DATABASE_URL=postgresql://aura_user:<strong-password>@db:5432/aura_db
REDIS_PASSWORD=<strong-password>
ADMIN_URL=secure-admin-xyz/
```

### 5. Déployer avec le Script

```bash
# Rendre le script exécutable (si ce n'est pas déjà fait)
chmod +x deploy.sh

# Déployer
./deploy.sh production
```

**Étapes du script :**
1. ✅ Validation de l'environnement
2. ✅ Vérification des dépendances
3. ✅ Création d'un backup
4. ✅ Construction des images Docker
5. ✅ Démarrage des services
6. ✅ Migrations de base de données
7. ✅ Collection des fichiers statiques
8. ✅ Vérifications système

### 6. Déploiement Manuel (Alternative)

```bash
# Construire les images
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Démarrer les services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Vérifier le statut
docker compose ps

# Voir les logs
docker compose logs -f
```

### 7. Créer un Superutilisateur

```bash
docker compose exec web python manage.py createsuperuser
```

---

## Maintenance

### Commandes Utiles

```bash
# Voir les logs
docker compose logs -f                    # Tous les services
docker compose logs -f web               # Service web uniquement
docker compose logs -f --tail=100 web    # 100 dernières lignes

# Statut des conteneurs
docker compose ps

# Redémarrer un service
docker compose restart web

# Shell dans un conteneur
docker compose exec web bash
docker compose exec db psql -U aura_user -d aura_db

# Exécuter des commandes Django
docker compose exec web python manage.py <command>

# Mise à jour des dépendances
docker compose exec web pip list --outdated
```

### Backups

#### Backup Automatique

```bash
# Backup complet
./backup.sh

# Backup database uniquement
./backup.sh --db-only

# Backup media uniquement
./backup.sh --media-only

# Backup et upload vers S3
./backup.sh --upload
```

#### Backup Manuel

**Database :**

```bash
# Backup
docker compose exec -T db pg_dump -U aura_user aura_db > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20250101.sql | docker compose exec -T db psql -U aura_user -d aura_db
```

**Media Files :**

```bash
# Backup
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Restore
tar -xzf media_backup_20250101.tar.gz
```

### Backup Automatisé avec Cron

```bash
# Éditer crontab
crontab -e

# Ajouter une ligne pour backup quotidien à 2h du matin
0 2 * * * cd /path/to/aura-app && ./backup.sh --upload >> /var/log/aura_backup.log 2>&1
```

### Mises à Jour

```bash
# 1. Créer un backup
./backup.sh

# 2. Pull les derniers changements
git pull origin main

# 3. Redéployer
./deploy.sh production
```

### Monitoring

#### Health Checks

```bash
# Check endpoint
curl http://localhost/health/

# Status Docker
docker compose ps

# Ressources utilisées
docker stats
```

#### Logs de Surveillance

```bash
# Erreurs Django
docker compose logs web | grep ERROR

# Erreurs Nginx
docker compose logs nginx | grep error

# Requêtes lentes
docker compose exec db psql -U aura_user -d aura_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

---

## Dépannage

### Problèmes Courants

#### 1. Les services ne démarrent pas

```bash
# Vérifier les logs
docker compose logs

# Vérifier l'état
docker compose ps

# Reconstruire les images
docker compose build --no-cache
docker compose up -d
```

#### 2. Erreur de connexion à la base de données

```bash
# Vérifier que PostgreSQL est prêt
docker compose exec db pg_isready -U aura_user

# Vérifier les variables d'environnement
docker compose exec web env | grep DATABASE

# Recréer le conteneur DB
docker compose down
docker volume rm aura-app_postgres_data  # ⚠️ Efface les données
docker compose up -d
```

#### 3. Erreur 502 Bad Gateway (Nginx)

```bash
# Vérifier que Django répond
docker compose exec web curl http://localhost:8000/health/

# Vérifier les logs Gunicorn
docker compose logs web

# Redémarrer le service web
docker compose restart web
```

#### 4. Static files ne chargent pas

```bash
# Recollect static files
docker compose exec web python manage.py collectstatic --clear --noinput

# Vérifier les permissions
docker compose exec web ls -la /app/staticfiles

# Vérifier la configuration Nginx
docker compose exec nginx cat /etc/nginx/nginx.conf
```

#### 5. Migrations échouent

```bash
# Voir les migrations en attente
docker compose exec web python manage.py showmigrations

# Fake une migration si nécessaire
docker compose exec web python manage.py migrate <app> <migration> --fake

# Recréer les migrations
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### Réinitialisation Complète (⚠️ DANGER)

```bash
# ⚠️ Ceci efface TOUTES les données !

# Arrêter et supprimer tout
docker compose down -v

# Supprimer les images
docker compose rm -f

# Reconstruire
docker compose build
docker compose up -d

# Réinitialiser la DB
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

---

## Commandes Makefile

Le [Makefile](Makefile) fournit des raccourcis pratiques :

```bash
make docker-build        # Construire les images
make docker-up           # Démarrer les services
make docker-down         # Arrêter les services
make docker-logs         # Voir les logs
make docker-shell        # Shell dans le conteneur web
make migrate-docker      # Exécuter les migrations
make superuser-docker    # Créer un superutilisateur
```

---

## Sécurité

### Checklist de Sécurité Production

- [ ] `DEBUG=False` dans `.env`
- [ ] `SECRET_KEY` unique et fort (50+ caractères)
- [ ] Mots de passe PostgreSQL et Redis forts
- [ ] SSL/TLS activé avec certificats valides
- [ ] Firewall configuré (ports 22, 80, 443 uniquement)
- [ ] `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` correctement configurés
- [ ] Admin URL personnalisée (`ADMIN_URL`)
- [ ] Backups automatisés configurés
- [ ] Monitoring activé
- [ ] Fichier `.env` avec permissions 600 (`chmod 600 .env`)
- [ ] Certificats SSL renouvelés automatiquement

### Renouvellement SSL (Let's Encrypt)

```bash
# Renouveler manuellement
sudo certbot renew

# Automatiser avec cron
sudo crontab -e
# Ajouter : 0 3 * * * certbot renew --quiet && docker compose restart nginx
```

---

## Support

Pour plus d'informations :

- **Documentation principale** : [README.md](README.md)
- **Schéma de base de données** : [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
- **Guide de migration** : [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

---

## Licence

[Voir LICENSE](LICENSE)
