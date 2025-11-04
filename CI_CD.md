# CI/CD Pipeline - Aura Art

Ce document décrit le système de CI/CD (Continuous Integration / Continuous Deployment) mis en place pour Aura Art avec GitHub Actions.

## Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Workflows](#workflows)
3. [Configuration](#configuration)
4. [Utilisation](#utilisation)
5. [Dépannage](#dépannage)

---

## Vue d'Ensemble

### Architecture CI/CD

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│                    (Code + Pull Requests)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌────────┐     ┌─────────┐    ┌──────────┐
    │   CI   │     │  Build  │    │   PR     │
    │ Tests  │     │ Docker  │    │  Checks  │
    └────┬───┘     └────┬────┘    └──────────┘
         │              │
         │              ▼
         │         ┌─────────────┐
         │         │   GHCR.io   │
         │         │   Docker    │
         │         │  Registry   │
         │         └─────┬───────┘
         │               │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │   Deploy      │
         │   Workflow    │
         └───────┬───────┘
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
    ┌─────────┐     ┌─────────┐
    │ Staging │     │  Prod   │
    │ Server  │     │ Server  │
    └─────────┘     └─────────┘
```

### Workflows Disponibles

| Workflow | Fichier | Déclencheur | Description |
|----------|---------|-------------|-------------|
| **CI Tests** | [ci.yml](.github/workflows/ci.yml) | Push, PR | Tests, linting, sécurité |
| **Build Docker** | [build-docker.yml](.github/workflows/build-docker.yml) | Push, PR, Tags | Build et push des images |
| **Deploy** | [deploy.yml](.github/workflows/deploy.yml) | Push main, Manuel | Déploiement automatisé |
| **PR Checks** | [pr-checks.yml](.github/workflows/pr-checks.yml) | Pull Request | Validation des PR |

---

## Workflows

### 1. CI - Tests & Quality ([ci.yml](.github/workflows/ci.yml))

**Déclencheurs :**
- Push sur `main` ou `develop`
- Pull Request vers `main` ou `develop`

**Jobs :**

#### 1.1. Lint (Qualité du Code)
- ✅ Black (formatage)
- ✅ isort (tri des imports)
- ✅ Flake8 (linting Python)
- ✅ Bandit (sécurité)
- ✅ Safety (vulnérabilités des dépendances)

#### 1.2. Test (Tests Unitaires)
- ✅ PostgreSQL 16 + Redis en services
- ✅ Migrations Django
- ✅ Tests avec pytest
- ✅ Coverage report (Codecov)

#### 1.3. Django Check
- ✅ `manage.py check --deploy`
- ✅ Vérifications de configuration production

#### 1.4. Security Audit
- ✅ Safety check (dépendances)
- ✅ Bandit scan (code)
- ✅ Rapport de sécurité

#### 1.5. Static Files Check
- ✅ `collectstatic` fonctionne
- ✅ Vérification des fichiers générés

**Durée estimée :** ~5-10 minutes

---

### 2. Build & Push Docker ([build-docker.yml](.github/workflows/build-docker.yml))

**Déclencheurs :**
- Push sur `main` ou `develop`
- Tags `v*` (releases)
- Pull Request vers `main`
- Manuel (`workflow_dispatch`)

**Jobs :**

#### 2.1. Build and Push
- ✅ Build multi-plateforme (amd64, arm64)
- ✅ Push vers GitHub Container Registry (GHCR)
- ✅ Images : `web` et `nginx`
- ✅ Tags automatiques :
  - `latest` (branche par défaut)
  - `main`, `develop` (branches)
  - `v1.0.0`, `v1.0`, `v1` (semantic versioning)
  - `main-sha123456` (commit SHA)
- ✅ Cache GitHub Actions
- ✅ Labels OCI (metadata)

#### 2.2. Security Scan
- ✅ Trivy scanner (vulnérabilités)
- ✅ Upload vers GitHub Security tab
- ✅ Scan CRITICAL et HIGH

#### 2.3. Test Docker Compose
- ✅ Démarrage de tous les services
- ✅ Health checks
- ✅ Tests de connectivité
- ✅ Upload logs si échec

**Images créées :**
```
ghcr.io/<votre-org>/aura-app/web:latest
ghcr.io/<votre-org>/aura-app/nginx:latest
```

**Durée estimée :** ~15-20 minutes

---

### 3. Deploy to Server ([deploy.yml](.github/workflows/deploy.yml))

**Déclencheurs :**
- Push sur `main` (auto-deploy production)
- Push sur `develop` (auto-deploy staging)
- Manuel avec choix d'environnement

**Jobs :**

#### 3.1. Pre-deployment Checks
- ✅ Validation Docker Compose
- ✅ Vérification des scripts
- ✅ Validation syntaxe bash

#### 3.2. Deploy to Staging
- ✅ Connexion SSH au serveur staging
- ✅ Backup automatique (base de données + media)
- ✅ Git pull
- ✅ Exécution de `./deploy.sh staging`
- ✅ Health check

**Environnement :** `staging`
**URL :** https://staging.aura-art.org

#### 3.3. Deploy to Production
- ✅ Connexion SSH au serveur production
- ✅ **Backup obligatoire** (avec upload S3)
- ✅ Git pull sur branche `main`
- ✅ Exécution de `./deploy.sh production`
- ✅ Health check approfondi
- ✅ Vérification SSL
- ✅ Création de tag de déploiement
- ✅ Rollback automatique en cas d'échec

**Environnement :** `production`
**URL :** https://aura-art.org

#### 3.4. Post-deployment Tests
- ✅ Health endpoint
- ✅ Home page
- ✅ API endpoints
- ✅ Static files
- ✅ Admin page
- ✅ Rapport dans GitHub Actions Summary

**Durée estimée :** ~5-10 minutes

**Secrets requis :** Voir [.github/SECRETS.md](.github/SECRETS.md)

---

### 4. Pull Request Checks ([pr-checks.yml](.github/workflows/pr-checks.yml))

**Déclencheurs :**
- Ouverture d'une PR
- Nouveau commit sur une PR
- PR marquée "Ready for review"

**Jobs :**

#### 4.1. PR Validation
- ✅ Format du titre (semantic commit)
- ✅ Détection des conflits de merge
- ✅ Vérification des fichiers trop gros (>5MB)

#### 4.2. Code Quality Report
- ✅ Complexité cyclomatique (radon)
- ✅ Maintainability Index
- ✅ Black, isort, Flake8
- ✅ Commentaire automatique avec résultats

#### 4.3. Security Scan
- ✅ Bandit scan
- ✅ TruffleHog (détection de secrets)

#### 4.4. Test Coverage
- ✅ Tests avec coverage
- ✅ Badge de couverture
- ✅ Rapport HTML
- ✅ Commentaire sur la PR

#### 4.5. Changed Files Analysis
- ✅ Liste des fichiers modifiés
- ✅ Détection de migrations Django
- ✅ Alerte si requirements.txt modifié
- ✅ Alerte si Dockerfile modifié

#### 4.6. PR Size Check
- ✅ Calcul de la taille de la PR
- ✅ Recommandations si trop grande

**Durée estimée :** ~8-15 minutes

---

## Configuration

### 1. Secrets GitHub

Voir la documentation complète : [.github/SECRETS.md](.github/SECRETS.md)

**Secrets requis minimum :**

```bash
# Déploiement Staging
STAGING_SSH_PRIVATE_KEY
STAGING_HOST
STAGING_USER

# Déploiement Production
PRODUCTION_SSH_PRIVATE_KEY
PRODUCTION_HOST
PRODUCTION_USER
```

### 2. Environments GitHub

Créez deux environments dans **Settings → Environments** :

**staging :**
- Protection : Aucune (déploiement automatique)
- Branch : `develop`

**production :**
- ✅ Required reviewers : 1+ reviewer
- ✅ Wait timer : 5 minutes (optionnel)
- ✅ Deployment branches : `main` uniquement

### 3. Branch Protection

Configurez les règles de protection dans **Settings → Branches** :

**Branch `main` :**
- ✅ Require pull request before merging
- ✅ Require status checks to pass
  - `lint`
  - `test`
  - `django-check`
  - `security`
- ✅ Require conversation resolution
- ✅ Require signed commits (recommandé)
- ✅ Include administrators

**Branch `develop` :**
- ✅ Require pull request before merging
- ✅ Require status checks to pass

### 4. GitHub Container Registry (GHCR)

Les images Docker sont automatiquement publiées sur GHCR.

**Accès :**
```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull image
docker pull ghcr.io/<org>/aura-app/web:latest
docker pull ghcr.io/<org>/aura-app/nginx:latest
```

**Configuration de visibilité :**
1. Allez sur **Packages** de votre repository
2. Cliquez sur l'image
3. **Package settings → Change visibility** → Public ou Private

---

## Utilisation

### Workflow Typique de Développement

#### 1. Créer une Feature Branch

```bash
git checkout -b feature/add-user-profile
# ... développement ...
git add .
git commit -m "feat: add user profile page"
git push origin feature/add-user-profile
```

#### 2. Créer une Pull Request

1. Allez sur GitHub
2. Cliquez sur **New Pull Request**
3. Sélectionnez `develop` comme base branch
4. Le workflow **PR Checks** s'exécute automatiquement
5. Vérifiez les résultats des checks

#### 3. Review & Merge

1. Un reviewer approuve la PR
2. Tous les checks sont verts ✅
3. Merge la PR dans `develop`
4. Le workflow **Build Docker** s'exécute
5. Le workflow **Deploy** déploie sur staging

#### 4. Release en Production

```bash
# Créer une PR de develop vers main
git checkout main
git pull origin main
git merge develop
git push origin main
```

1. Le workflow **Build Docker** build les images
2. Le workflow **Deploy** déclenche le déploiement production
3. **Approbation requise** (si configuré)
4. Déploiement automatique après approbation

### Déploiement Manuel

#### Via GitHub Actions UI

1. Allez dans **Actions → Deploy to Server**
2. Cliquez sur **Run workflow**
3. Sélectionnez :
   - Branch : `main` ou `develop`
   - Environment : `staging` ou `production`
   - Skip backup : `false` (recommandé)
4. Cliquez sur **Run workflow**

#### Via GitHub CLI

```bash
# Installer gh CLI
brew install gh  # macOS
# ou apt install gh  # Linux

# Déployer en staging
gh workflow run deploy.yml -f environment=staging

# Déployer en production
gh workflow run deploy.yml -f environment=production
```

#### SSH Manuel (Backup)

```bash
# Se connecter au serveur
ssh deploy@aura-art.org

# Aller dans le répertoire
cd /var/www/aura-app

# Déployer
./deploy.sh production
```

### Rollback en Production

En cas de problème après déploiement :

#### Option 1 : Via Git

```bash
# Sur le serveur
cd /var/www/aura-app
git log --oneline  # Trouver le commit précédent
git checkout <commit-hash>
./deploy.sh production
```

#### Option 2 : Restaurer un Backup

```bash
# Lister les backups
ls -lah backups/

# Restaurer la base de données
./backup.sh --restore backups/aura_backup_20250101_120000_db.sql.gz

# Redémarrer les services
docker compose restart
```

#### Option 3 : Redéployer une version précédente

1. Allez sur GitHub → **Releases**
2. Trouvez la version précédente (ex: `v1.0.0`)
3. Allez dans **Actions → Deploy**
4. Run workflow sur le tag `v1.0.0`

---

## Monitoring & Alertes

### Voir les Workflows en Cours

```bash
# Via GitHub CLI
gh run list --limit 10

# Voir les détails d'un run
gh run view <run-id>

# Voir les logs
gh run view <run-id> --log
```

### Notifications

Configurez les notifications dans **Settings → Notifications** :

- ✅ Workflow runs (succès et échecs)
- ✅ Deployment status
- ✅ Security alerts

### Badges dans README

Ajoutez des badges pour visualiser le statut :

```markdown
![CI](https://github.com/<org>/aura-app/workflows/CI/badge.svg)
![Docker Build](https://github.com/<org>/aura-app/workflows/Build%20Docker/badge.svg)
![Deploy](https://github.com/<org>/aura-app/workflows/Deploy/badge.svg)
```

---

## Dépannage

### Workflow Échoue - "Permission denied (publickey)"

**Cause :** Clé SSH incorrecte ou manquante

**Solution :**
1. Vérifiez que le secret `PRODUCTION_SSH_PRIVATE_KEY` est bien configuré
2. Testez la connexion SSH manuellement
3. Vérifiez les permissions sur le serveur

```bash
# Sur le serveur
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Build Docker Échoue

**Cause :** Erreur dans le Dockerfile ou dépendances manquantes

**Solution :**
1. Testez le build localement : `docker build -t test .`
2. Vérifiez les logs du workflow
3. Vérifiez que `requirements.txt` est à jour

### Tests Échouent

**Cause :** Erreur dans le code ou tests cassés

**Solution :**
1. Exécutez les tests localement : `pytest`
2. Vérifiez la base de données de test
3. Vérifiez les logs du workflow

### Déploiement Échoue - Health Check Failed

**Cause :** Application ne démarre pas correctement

**Solution :**
1. Connectez-vous au serveur
2. Vérifiez les logs : `docker compose logs -f web`
3. Vérifiez les variables d'environnement
4. Vérifiez la base de données

```bash
# Sur le serveur
docker compose ps
docker compose logs web --tail=100
docker compose exec web python manage.py check
```

### Secrets Non Reconnus

**Cause :** Secrets mal configurés ou nom incorrect

**Solution :**
1. Vérifiez l'orthographe exacte du secret
2. Vérifiez le scope (repository vs environment)
3. Re-créez le secret si nécessaire

---

## Bonnes Pratiques

### ✅ Faire

- Toujours créer une PR pour les changements
- Attendre que tous les checks soient verts avant de merger
- Tester localement avant de push
- Écrire des tests pour le nouveau code
- Utiliser des commits semantiques (`feat:`, `fix:`, `docs:`)
- Créer des backups avant les déploiements importants
- Monitorer les logs après déploiement

### ❌ Éviter

- Merger des PR avec des checks en échec
- Déployer directement en production sans passer par staging
- Skip les tests pour "gagner du temps"
- Commiter des secrets ou mots de passe
- Push directement sur `main` sans PR
- Déployer sans backup
- Ignorer les alertes de sécurité

---

## Métriques & Analytics

### GitHub Insights

Consultez **Insights → Actions** pour voir :
- Temps d'exécution moyen des workflows
- Taux de succès/échec
- Usage des minutes GitHub Actions

### Coverage Trends

Le coverage des tests est uploadé sur Codecov :
- Voir l'évolution du coverage dans le temps
- Identifier les fichiers non couverts
- Configurer des objectifs de coverage

---

## Coûts GitHub Actions

GitHub offre :
- **2,000 minutes/mois** gratuites pour les repos publics
- **Unlimited** pour les repos publics

Nos workflows consomment environ :
- CI : ~10 minutes par run
- Build Docker : ~20 minutes par run
- Deploy : ~5 minutes par run

**Estimation mensuelle** (20 PR + 40 commits) :
- ~1,500 minutes/mois
- Gratuit pour repos public
- ~$8-15/mois pour repos privé

**Optimisations :**
- Utilisation de cache GitHub
- Build conditionnels (skip si docs uniquement)
- Workflows parallèles

---

## Roadmap CI/CD

### Améliorations Futures

- [ ] Déploiement Kubernetes (optionnel)
- [ ] Tests end-to-end (Playwright, Selenium)
- [ ] Performance testing (Lighthouse CI)
- [ ] Infrastructure as Code (Terraform)
- [ ] GitOps avec ArgoCD
- [ ] Monitoring avancé (Prometheus + Grafana)
- [ ] Notifications Slack/Discord
- [ ] Auto-rollback automatique
- [ ] Canary deployments
- [ ] A/B testing infrastructure

---

## Ressources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Secrets Management](.github/SECRETS.md)
- [Deployment Guide](DOCKER_DEPLOYMENT.md)
- [Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

---

**Dernière mise à jour :** 2025-01-04
