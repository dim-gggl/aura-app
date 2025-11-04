# GitHub Actions Workflows

Ce répertoire contient tous les workflows GitHub Actions pour l'automatisation CI/CD d'Aura Art.

## 📁 Structure

```
.github/
├── workflows/
│   ├── ci.yml              # Tests, linting, sécurité
│   ├── build-docker.yml    # Build et push des images Docker
│   ├── deploy.yml          # Déploiement automatisé
│   ├── pr-checks.yml       # Vérifications des Pull Requests
│   └── release.yml         # Création de releases GitHub
├── SECRETS.md              # Documentation des secrets requis
└── README.md               # Ce fichier
```

## 🔄 Workflows

### 1. CI - Tests & Quality ([ci.yml](workflows/ci.yml))

**Déclencheurs:**
- Push sur `main` ou `develop`
- Pull Requests vers `main` ou `develop`

**Actions:**
- ✅ Linting (Black, isort, Flake8)
- ✅ Tests unitaires avec coverage
- ✅ Vérifications Django
- ✅ Audit de sécurité (Bandit, Safety)
- ✅ Vérification des static files

**Durée:** ~8-12 minutes

---

### 2. Build & Push Docker ([build-docker.yml](workflows/build-docker.yml))

**Déclencheurs:**
- Push sur `main` ou `develop`
- Tags `v*`
- Pull Requests (build uniquement)
- Manuel

**Actions:**
- ✅ Build multi-plateforme (amd64, arm64)
- ✅ Push vers GitHub Container Registry
- ✅ Scan de sécurité avec Trivy
- ✅ Test Docker Compose

**Images:**
- `ghcr.io/<org>/aura-app/web:latest`
- `ghcr.io/<org>/aura-app/nginx:latest`

**Durée:** ~15-20 minutes

---

### 3. Deploy ([deploy.yml](workflows/deploy.yml))

**Déclencheurs:**
- Push sur `main` → Déploie en production
- Push sur `develop` → Déploie en staging
- Manuel avec choix d'environnement

**Actions:**
- ✅ Pre-deployment checks
- ✅ Backup automatique
- ✅ Connexion SSH
- ✅ Exécution de `deploy.sh`
- ✅ Health checks
- ✅ Post-deployment tests

**Environnements:**
- **Staging:** https://staging.aura-art.org
- **Production:** https://aura-art.org (avec approbation)

**Durée:** ~5-10 minutes

---

### 4. PR Checks ([pr-checks.yml](workflows/pr-checks.yml))

**Déclencheurs:**
- Ouverture d'une PR
- Nouveau commit sur une PR
- PR marquée "ready for review"

**Actions:**
- ✅ Validation du format de PR
- ✅ Rapport de qualité de code
- ✅ Scan de sécurité (Bandit, TruffleHog)
- ✅ Test coverage avec commentaire
- ✅ Analyse des fichiers modifiés
- ✅ Vérification de la taille de la PR

**Durée:** ~10-15 minutes

---

### 5. Release ([release.yml](workflows/release.yml))

**Déclencheurs:**
- Push d'un tag `v*`
- Manuel avec version spécifiée

**Actions:**
- ✅ Création de GitHub Release
- ✅ Génération du changelog
- ✅ Build des images Docker avec tags versionnés
- ✅ Création d'archives (source + deployment)
- ✅ Génération de checksums
- ✅ Notification

**Durée:** ~20-25 minutes

---

## 🔐 Configuration des Secrets

Voir [SECRETS.md](SECRETS.md) pour la documentation complète.

**Secrets minimum requis:**

```bash
# Staging
STAGING_SSH_PRIVATE_KEY
STAGING_HOST
STAGING_USER

# Production
PRODUCTION_SSH_PRIVATE_KEY
PRODUCTION_HOST
PRODUCTION_USER
```

## 🚀 Utilisation

### Pour les Développeurs

1. **Créer une feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Développer et commiter:**
   ```bash
   git commit -m "feat: add new feature"
   git push origin feature/my-feature
   ```

3. **Créer une Pull Request:**
   - Le workflow `pr-checks.yml` s'exécute automatiquement
   - Vérifiez que tous les checks sont verts ✅

4. **Merge la PR:**
   - Après review et approbation
   - Le merge déclenche les workflows de build et déploiement

### Pour les Releases

**Créer une nouvelle release:**

```bash
# Créer un tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

Le workflow `release.yml` crée automatiquement:
- GitHub Release avec changelog
- Images Docker taggées
- Archives pour déploiement
- Checksums

### Déploiement Manuel

**Via GitHub UI:**
1. Actions → Deploy to Server
2. Run workflow
3. Choisir l'environnement
4. Run workflow

**Via GitHub CLI:**
```bash
gh workflow run deploy.yml -f environment=production
```

## 📊 Monitoring

### Voir les Workflows

**Via GitHub UI:**
- Actions → Workflows

**Via GitHub CLI:**
```bash
# Lister les runs récents
gh run list --limit 10

# Voir les détails
gh run view <run-id>

# Voir les logs
gh run view <run-id> --log

# Re-run un workflow
gh run rerun <run-id>
```

### Badges de Statut

Ajoutez ces badges dans votre README principal:

```markdown
![CI](https://github.com/<org>/aura-app/workflows/CI/badge.svg)
![Build](https://github.com/<org>/aura-app/workflows/Build%20Docker/badge.svg)
![Deploy](https://github.com/<org>/aura-app/workflows/Deploy/badge.svg)
```

## 🔧 Maintenance

### Mettre à Jour un Workflow

1. Éditez le fichier `.yml` dans `.github/workflows/`
2. Testez localement si possible
3. Commitez et push
4. Le workflow met à jour automatiquement

### Désactiver un Workflow Temporairement

**Via GitHub UI:**
1. Actions → Workflows
2. Sélectionner le workflow
3. "..." → Disable workflow

**Via GitHub CLI:**
```bash
gh workflow disable <workflow-name>
gh workflow enable <workflow-name>
```

### Debug un Workflow

1. Activer le debug logging:
   ```bash
   # Ajouter ces secrets au repository
   ACTIONS_RUNNER_DEBUG=true
   ACTIONS_STEP_DEBUG=true
   ```

2. Re-run le workflow avec debug activé

3. Consulter les logs détaillés

## 📚 Documentation Complète

- **CI/CD Guide:** [../CI_CD.md](../CI_CD.md)
- **Secrets Config:** [SECRETS.md](SECRETS.md)
- **Docker Deployment:** [../DOCKER_DEPLOYMENT.md](../DOCKER_DEPLOYMENT.md)

## 🎯 Bonnes Pratiques

### ✅ Faire

- Tester localement avant de push
- Attendre les checks verts avant de merger
- Utiliser des commits sémantiques
- Créer des PR de taille raisonnable (<500 lignes)
- Documenter les changements importants

### ❌ Éviter

- Skip les tests pour gagner du temps
- Merger avec des checks en échec
- Commiter des secrets
- Push directement sur `main`
- Créer des PR géantes (>1000 lignes)

## 🐛 Dépannage

### Workflow Bloqué

**Symptôme:** Workflow en attente indéfiniment

**Solution:**
1. Vérifier les runners disponibles
2. Annuler et re-run le workflow
3. Vérifier les limites GitHub Actions

### Tests Échouent dans CI mais Passent Localement

**Causes possibles:**
- Différence Python/PostgreSQL/Redis versions
- Variables d'environnement manquantes
- Dépendances système manquantes

**Solution:**
1. Vérifier les versions dans `ci.yml`
2. Comparer avec votre environnement local
3. Ajouter les dépendances nécessaires

### Déploiement Échoue

**Causes possibles:**
- Secrets SSH incorrects
- Serveur inaccessible
- Erreur dans `deploy.sh`

**Solution:**
1. Vérifier les logs du workflow
2. Tester la connexion SSH manuellement
3. Vérifier l'état du serveur
4. Consulter [SECRETS.md](SECRETS.md)

## 🔄 Workflow Dependencies

```
PR Created
    ↓
pr-checks.yml ─────────────────────┐
    ↓                              │
PR Merged                          │
    ↓                              ↓
ci.yml ────────────┐           (Coverage)
    ↓              │
build-docker.yml ←─┘
    ↓
deploy.yml
    ↓
(Production/Staging)

Tag Pushed
    ↓
release.yml
    ↓
(GitHub Release + Docker Images)
```

## 📈 Métriques

Consultez **Insights → Actions** pour:
- Temps d'exécution moyen
- Taux de succès/échec
- Usage des minutes GitHub Actions
- Tendances dans le temps

## 🤝 Contribution

Pour améliorer les workflows:

1. Créer une PR avec les modifications
2. Documenter les changements
3. Tester avec un workflow test si possible
4. Demander une review

## 📞 Support

- **Issues GitHub:** [Issues](https://github.com/<org>/aura-app/issues)
- **Discussions:** [Discussions](https://github.com/<org>/aura-app/discussions)
- **Documentation:** [CI_CD.md](../CI_CD.md)

---

**Dernière mise à jour:** 2025-01-04
