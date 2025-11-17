# ✅ Checklist : Configuration R2 privé pour Railway

## 📋 Étapes de configuration

### 1️⃣ Cloudflare R2 - Création du bucket PRIVÉ

- [ ] Se connecter à [Cloudflare Dashboard](https://dash.cloudflare.com/)
- [ ] Aller dans **R2 Object Storage** (menu latéral)
- [ ] Cliquer sur **Create bucket**
- [ ] Nom du bucket : `aura-app-media-private`
- [ ] ⚠️ **NE PAS cocher "Allow Public Access"**
- [ ] Créer le bucket

---

### 2️⃣ Cloudflare R2 - Génération des clés API

- [ ] Dans R2 → **Manage R2 API Tokens**
- [ ] Cliquer sur **Create API Token**
- [ ] Configurer le token :
  - [ ] **Token name** : `aura-app-production`
  - [ ] **Permissions** : `Object Read & Write`
  - [ ] **Apply to specific buckets only** : Sélectionner `aura-app-media-private`
  - [ ] **TTL** : Pas d'expiration (ou selon votre politique de sécurité)
- [ ] Cliquer sur **Create API Token**
- [ ] **COPIER ET SAUVEGARDER** (vous ne pourrez plus les voir !) :
  - [ ] Access Key ID : `____________________`
  - [ ] Secret Access Key : `____________________`
  - [ ] Endpoint URL : `https://<account-id>.r2.cloudflarestorage.com`

---

### 3️⃣ Railway - Configuration des variables d'environnement

- [ ] Se connecter à [Railway](https://railway.app/)
- [ ] Sélectionner le projet `aura-app`
- [ ] Aller dans **Variables**
- [ ] Ajouter les variables suivantes :

```bash
AWS_STORAGE_BUCKET_NAME=aura-app-media-private
AWS_ACCESS_KEY_ID=<coller-votre-access-key-id>
AWS_SECRET_ACCESS_KEY=<coller-votre-secret-access-key>
AWS_S3_REGION_NAME=auto
AWS_S3_ENDPOINT_URL=https://<votre-account-id>.r2.cloudflarestorage.com
```

- [ ] Sauvegarder

---

### 4️⃣ Code Django - Modifications

#### A. Modifier `aura_app/settings/production.py` (lignes 113-122)

- [ ] Ouvrir le fichier `aura_app/settings/production.py`
- [ ] Trouver la section `if STORAGES["default"]["BACKEND"].endswith("S3Boto3Storage"):`
- [ ] Remplacer par le code de [PRODUCTION_SETTINGS_CHANGES.md](./PRODUCTION_SETTINGS_CHANGES.md#modification-1--configuration-s3r2-lignes-113-122)

**Résumé des changements :**
- [ ] Ajouter `AWS_QUERYSTRING_AUTH = True`
- [ ] Ajouter `AWS_QUERYSTRING_EXPIRE = 3600`
- [ ] Ajouter `AWS_S3_FILE_OVERWRITE = False`
- [ ] Changer `CacheControl` de `"public"` à `"private"`
- [ ] Ajouter `"ContentDisposition": "inline"`

#### B. Modifier la CSP (Content Security Policy)

- [ ] Dans le même fichier, trouver la section `"img-src":` (vers ligne 183)
- [ ] Ajouter votre endpoint R2 :

```python
"img-src": (
    "'self'",
    "data:",
    "blob:",
    "https://<votre-account-id>.r2.cloudflarestorage.com",  # ← AJOUTER
),
```

---

### 5️⃣ Déploiement

- [ ] Commiter les modifications :
```bash
git add aura_app/settings/production.py
git commit -m "Configure private R2 storage with signed URLs"
```

- [ ] Pousser sur Railway :
```bash
git push
```

- [ ] Vérifier le déploiement dans Railway Dashboard
- [ ] Attendre que le build soit terminé ✅

---

### 6️⃣ Tests de validation

#### Test 1 : Upload d'une image
- [ ] Se connecter à l'admin Django en production
- [ ] Aller dans **Artworks** → Ajouter une œuvre
- [ ] Uploader une photo
- [ ] Sauvegarder

#### Test 2 : Vérifier le stockage R2
- [ ] Aller dans le dashboard Cloudflare R2
- [ ] Ouvrir le bucket `aura-app-media-private`
- [ ] Vérifier que le fichier `artworks/nom-du-fichier.jpg` est présent

#### Test 3 : Vérifier l'accès privé avec URLs signées
- [ ] Aller sur la page de détail de l'œuvre
- [ ] Clic droit sur l'image → **Copier l'adresse de l'image**
- [ ] L'URL doit contenir des paramètres de signature :
  ```
  ?AWSAccessKeyId=...&Signature=...&Expires=...
  ```
- [ ] ✅ Si oui : configuration réussie !

#### Test 4 : Vérifier que l'accès est vraiment privé
- [ ] Copier l'URL de l'image
- [ ] Supprimer tous les paramètres après `?` (garder juste l'URL de base)
- [ ] Essayer d'accéder à cette URL sans signature
- [ ] ✅ Vous devez obtenir une erreur **403 Forbidden**

#### Test 5 : Vérifier l'expiration des URLs
- [ ] Copier une URL signée complète
- [ ] Attendre 1 heure (ou modifier `AWS_QUERYSTRING_EXPIRE` pour tester plus vite)
- [ ] Essayer d'accéder à l'URL expirée
- [ ] ✅ Vous devez obtenir une erreur d'accès

---

## 🔍 Dépannage

### Erreur : Images ne s'affichent pas (CSP)
**Symptôme :** Console navigateur : `Refused to load the image because it violates the Content Security Policy`

**Solution :**
- Vérifier que l'endpoint R2 est bien dans la directive `img-src` de la CSP
- Redéployer après modification

### Erreur : 403 Forbidden sur toutes les images
**Symptôme :** Aucune image ne charge, même avec signature

**Solutions à vérifier :**
1. Les clés API sont correctes dans Railway
2. Le bucket existe et est bien privé
3. Le token API a les permissions `Object Read & Write`
4. `AWS_QUERYSTRING_AUTH = True` est bien dans le code

### Erreur : "No module named 'storages'"
**Symptôme :** Erreur au démarrage de Django

**Solution :**
```bash
pip install django-storages[s3] boto3
```
Mais normalement, c'est déjà dans votre `requirements.txt` ✅

### Les images restent accessibles sans signature
**Symptôme :** L'URL sans paramètres fonctionne encore

**Solutions :**
1. Vérifier que le bucket R2 est bien **privé** (pas de public access)
2. Vérifier que `AWS_DEFAULT_ACL = None` (pas `public-read`)
3. Supprimer et recréer le bucket si nécessaire

---

## 📊 Vérifications post-déploiement

| Vérification | Statut | Notes |
|--------------|--------|-------|
| Bucket R2 créé et privé | ⬜ | |
| Variables Railway configurées | ⬜ | |
| Code Django modifié | ⬜ | |
| CSP mise à jour | ⬜ | |
| Upload d'image fonctionne | ⬜ | |
| Image visible avec signature | ⬜ | |
| Image bloquée sans signature (403) | ⬜ | |
| URL expire après 1h | ⬜ | |

---

## 📚 Documentation de référence

- [Guide complet R2](./RAILWAY_R2_SETUP.md)
- [Modifications code](./PRODUCTION_SETTINGS_CHANGES.md)
- [Django Storages Doc](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)
- [Cloudflare R2 Doc](https://developers.cloudflare.com/r2/)
