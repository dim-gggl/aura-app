# GitHub Secrets Configuration

Ce document liste tous les secrets GitHub nécessaires pour les workflows CI/CD.

## Configuration des Secrets

Allez dans **Settings → Secrets and variables → Actions** de votre repository GitHub pour ajouter ces secrets.

---

## 🔐 Secrets Requis

### Deployment - SSH Access

#### Staging Environment

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `STAGING_SSH_PRIVATE_KEY` | Clé SSH privée pour accéder au serveur staging | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `STAGING_HOST` | Hostname ou IP du serveur staging | `staging.aura-app.org` ou `192.168.1.100` |
| `STAGING_USER` | Utilisateur SSH sur le serveur staging | `deploy` ou `ubuntu` |

#### Production Environment

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `PRODUCTION_SSH_PRIVATE_KEY` | Clé SSH privée pour accéder au serveur production | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `PRODUCTION_HOST` | Hostname ou IP du serveur production | `aura-app.org` ou `192.168.1.200` |
| `PRODUCTION_USER` | Utilisateur SSH sur le serveur production | `deploy` ou `ubuntu` |

### Docker Registry (Optionnel)

Si vous utilisez Docker Hub en plus de GitHub Container Registry :

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKERHUB_USERNAME` | Nom d'utilisateur Docker Hub | `myusername` |
| `DOCKERHUB_TOKEN` | Token d'accès Docker Hub | `dckr_pat_xxxxxxxxxxxxx` |

---

## 🔑 Comment Générer les Secrets

### 1. Clés SSH pour le Déploiement

Sur votre machine locale :

```bash
# Générer une nouvelle paire de clés SSH pour le déploiement
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key

# Copier la clé publique sur le serveur
ssh-copy-id -i ~/.ssh/github_deploy_key.pub user@server

# Afficher la clé privée (à copier dans GitHub Secrets)
cat ~/.ssh/github_deploy_key
```

**⚠️ Important :**
- Ne partagez JAMAIS votre clé privée
- Ajoutez la clé privée complète (incluant `-----BEGIN` et `-----END`)
- Testez la connexion SSH avant de l'utiliser dans GitHub Actions

### 2. Token Docker Hub (Optionnel)

1. Connectez-vous sur [hub.docker.com](https://hub.docker.com)
2. Allez dans **Account Settings → Security**
3. Cliquez sur **New Access Token**
4. Donnez un nom descriptif : `github-actions-aura-app`
5. Sélectionnez les permissions : `Read & Write`
6. Copiez le token généré

---

## 🔧 Configuration des Secrets dans GitHub

### Via l'Interface Web

1. Allez sur votre repository GitHub
2. Cliquez sur **Settings** (onglet)
3. Dans le menu latéral, cliquez sur **Secrets and variables → Actions**
4. Cliquez sur **New repository secret**
5. Ajoutez le nom et la valeur du secret
6. Cliquez sur **Add secret**

### Via GitHub CLI

```bash
# Installation de gh CLI
# macOS: brew install gh
# Linux: voir https://cli.github.com/

# Authentification
gh auth login

# Ajouter un secret
gh secret set STAGING_SSH_PRIVATE_KEY < ~/.ssh/github_deploy_key
gh secret set STAGING_HOST -b "staging.aura-app.org"
gh secret set STAGING_USER -b "deploy"

# Même chose pour production
gh secret set PRODUCTION_SSH_PRIVATE_KEY < ~/.ssh/github_deploy_key_prod
gh secret set PRODUCTION_HOST -b "aura-app.org"
gh secret set PRODUCTION_USER -b "deploy"
```

---

## 🌍 Environments Configuration

Pour une meilleure sécurité, configurez des **Environments** dans GitHub :

### Créer les Environments

1. Allez dans **Settings → Environments**
2. Créez deux environments :
   - `staging`
   - `production`

### Configuration de l'Environment Production

Pour l'environment `production`, ajoutez des protections :

- ✅ **Required reviewers** : Exiger une approbation avant le déploiement
- ✅ **Wait timer** : Délai avant le déploiement (ex: 5 minutes)
- ✅ **Deployment branches** : Limiter aux branches `main` uniquement

### Ajouter des Secrets par Environment

Vous pouvez également ajouter des secrets spécifiques à chaque environment :

**Staging Environment Secrets :**
- `DATABASE_URL`
- `SECRET_KEY`
- `AWS_ACCESS_KEY_ID`
- etc.

**Production Environment Secrets :**
- `DATABASE_URL`
- `SECRET_KEY`
- `AWS_ACCESS_KEY_ID`
- etc.

---

## 🧪 Tester la Configuration SSH

Avant de configurer les secrets GitHub, testez votre connexion SSH :

```bash
# Test avec la clé de déploiement
ssh -i ~/.ssh/github_deploy_key user@server

# Si ça fonctionne, testez la commande de déploiement
ssh -i ~/.ssh/github_deploy_key user@server "cd /var/www/aura-app && ./deploy.sh staging"
```

---

## 🔒 Bonnes Pratiques de Sécurité

### 1. Clés SSH Dédiées

- ✅ Créez des clés SSH **dédiées uniquement au déploiement**
- ✅ N'utilisez **pas** votre clé SSH personnelle
- ✅ Utilisez des clés différentes pour staging et production
- ✅ Limitez les permissions du user SSH (pas de `sudo` si possible)

### 2. Rotation des Secrets

- 🔄 Changez les clés SSH tous les 6-12 mois
- 🔄 Changez les tokens Docker Hub si compromis
- 🔄 Auditez les secrets régulièrement

### 3. Permissions Minimales

Le user SSH de déploiement devrait avoir :

```bash
# Créer un user dédié au déploiement
sudo adduser deploy

# Donner ownership du répertoire de l'app
sudo chown -R deploy:deploy /var/www/aura-app

# Autoriser Docker sans sudo (optionnel)
sudo usermod -aG docker deploy

# NE PAS donner sudo complet
```

### 4. Audit des Secrets

Vérifiez régulièrement quels secrets sont utilisés :

```bash
# Lister les secrets du repository
gh secret list

# Voir les dernières utilisations dans Actions
# GitHub UI: Actions → Workflows → View logs
```

---

## 📋 Checklist de Configuration

Avant de déployer, vérifiez que :

- [ ] Clés SSH générées et testées
- [ ] Clés publiques SSH ajoutées sur les serveurs
- [ ] Secrets GitHub configurés (staging et production)
- [ ] Environments GitHub créés (staging et production)
- [ ] Protections de branche activées (production)
- [ ] Connexion SSH testée depuis votre machine
- [ ] User de déploiement créé sur les serveurs
- [ ] Permissions correctes sur `/var/www/aura-app`
- [ ] Docker accessible sans sudo (optionnel)
- [ ] Workflow de test exécuté avec succès

---

## 🐛 Dépannage

### Erreur "Permission denied (publickey)"

```bash
# Vérifier que la clé est bien copiée sur le serveur
ssh-copy-id -i ~/.ssh/github_deploy_key.pub user@server

# Vérifier les permissions
chmod 600 ~/.ssh/github_deploy_key
chmod 644 ~/.ssh/github_deploy_key.pub

# Tester avec verbose
ssh -v -i ~/.ssh/github_deploy_key user@server
```

### Erreur "Host key verification failed"

Sur le serveur GitHub Actions, ajoutez l'host aux known_hosts :

```yaml
- name: Add server to known_hosts
  run: |
    mkdir -p ~/.ssh
    ssh-keyscan -H ${{ secrets.PRODUCTION_HOST }} >> ~/.ssh/known_hosts
```

### Secret non reconnu dans le workflow

Vérifiez :
1. Le nom du secret est exact (case-sensitive)
2. Le secret est bien dans le bon scope (repository ou environment)
3. Le workflow a les permissions nécessaires

---

## 📚 Ressources

- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [SSH Key Generation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
- [GitHub CLI](https://cli.github.com/)

---

## 🆘 Support

En cas de problème avec les secrets ou le déploiement :

1. Vérifiez les logs des workflows GitHub Actions
2. Testez manuellement la connexion SSH
3. Vérifiez que les secrets sont bien configurés
4. Consultez ce guide et la documentation GitHub

---

**Note de Sécurité :**

❌ **Ne committez JAMAIS** de secrets dans le code
❌ **Ne partagez JAMAIS** vos clés privées
❌ **Ne loguez JAMAIS** les secrets dans les workflows
✅ **Utilisez toujours** les GitHub Secrets
✅ **Auditez régulièrement** les accès et permissions
✅ **Activez** l'authentification à deux facteurs sur GitHub
