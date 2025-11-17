# Configuration Cloudflare R2 pour stockage privé sur Railway

## Pourquoi R2 ?

Railway utilise un système de fichiers **éphémère** : tous les fichiers uploadés dans `/media/` sont perdus à chaque redéploiement. R2 offre un stockage persistant et privé.

---

## 🔒 Configuration pour accès PRIVÉ avec URLs signées

### Étape 1 : Créer le bucket R2 (PRIVÉ)

1. Connectez-vous à [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Menu latéral → **R2 Object Storage**
3. **Create bucket**
4. Nom : `aura-app-media-private`
5. ⚠️ **IMPORTANT** : Ne cochez PAS "Allow Public Access"
6. Créez le bucket

### Étape 2 : Générer les clés API R2

1. Dans R2 → **Manage R2 API Tokens**
2. **Create API Token**
3. Configuration :
   - **Token name** : `aura-app-production`
   - **Permissions** : `Object Read & Write`
   - **Bucket** : `aura-app-media-private`
   - **TTL** : Pas d'expiration
4. **COPIEZ ET SAUVEGARDEZ** :
   - Access Key ID
   - Secret Access Key
   - Endpoint URL : `https://<account-id>.r2.cloudflarestorage.com`

⚠️ Le Secret Access Key ne sera plus visible après !

### Étape 3 : Variables d'environnement Railway

Ajoutez ces variables dans Railway :

```bash
AWS_STORAGE_BUCKET_NAME=aura-app-media-private
AWS_ACCESS_KEY_ID=<votre-access-key-id>
AWS_SECRET_ACCESS_KEY=<votre-secret-access-key>
AWS_S3_REGION_NAME=auto
AWS_S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
```

---

## 📝 Modifications Django requises

### Dans `aura_app/settings/production.py`

Remplacez la section `if STORAGES["default"]["BACKEND"].endswith("S3Boto3Storage"):` (lignes 113-119) par :

```python
if STORAGES["default"]["BACKEND"].endswith("S3Boto3Storage"):
    # Configuration pour accès PRIVÉ avec URLs signées
    AWS_DEFAULT_ACL = None  # Pas d'ACL publique
    AWS_QUERYSTRING_AUTH = True  # Active les URLs signées temporaires
    AWS_S3_FILE_OVERWRITE = False  # Évite l'écrasement accidentel

    # Durée de validité des URLs signées (1 heure = 3600 secondes)
    AWS_QUERYSTRING_EXPIRE = 3600

    # Pas de cache public pour les fichiers privés
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "private, max-age=3600",
        "ContentDisposition": "inline",  # Affiche dans le navigateur
    }

    # MEDIA_URL pour compatibilité (mais les URLs seront signées dynamiquement)
    if AWS_S3_ENDPOINT_URL and AWS_STORAGE_BUCKET_NAME:
        MEDIA_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/"
    elif AWS_STORAGE_BUCKET_NAME:
        MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"
```

### Mise à jour CSP pour autoriser R2

Dans `aura_app/settings/production.py`, ligne 183-187, ajoutez votre endpoint R2 :

```python
"img-src": (
    "'self'",
    "data:",
    "blob:",
    "https://<account-id>.r2.cloudflarestorage.com",  # ← Ajoutez cette ligne
),
```

---

## 🧪 Comment tester

### 1. Vérifier la configuration locale

```bash
# Testez que django-storages est installé
pip list | grep django-storages
# Si absent : pip install django-storages[s3] boto3
```

### 2. Tester l'upload

1. Déployez sur Railway
2. Connectez-vous à l'admin Django
3. Ajoutez une œuvre avec une photo
4. Vérifiez dans le dashboard R2 que le fichier apparaît dans le bucket

### 3. Vérifier l'accès privé

Dans le template, `{{ photo.image.url }}` génèrera une URL signée comme :

```
https://<account-id>.r2.cloudflarestorage.com/aura-app-media-private/artworks/photo.jpg?
AWSAccessKeyId=xxx&Signature=yyy&Expires=1234567890
```

**Test d'accès privé :**
- ✅ L'URL avec signature → image visible
- ❌ L'URL sans paramètres `?AWSAccessKeyId=...` → erreur 403 Forbidden

---

## 🔐 Sécurité des URLs signées

**Comment ça marche :**
- Django génère une URL temporaire avec signature cryptographique
- L'URL expire après 1 heure (configurable avec `AWS_QUERYSTRING_EXPIRE`)
- Sans signature valide → accès refusé (403)

**Avantages :**
- Pas besoin de proxy Django pour servir les images
- Les fichiers restent strictement privés
- Performance : R2 sert directement les fichiers

**Limites :**
- L'URL peut être partagée (mais expire après 1h)
- Si besoin d'URLs permanentes → implémenter une vue Django proxy

---

## 📊 Coûts Cloudflare R2

**Offre gratuite :**
- 10 GB de stockage
- Opérations classe A : 1M/mois
- Opérations classe B : 10M/mois
- Pas de frais de sortie (egress)

Pour une app de gestion d'œuvres d'art, c'est largement suffisant !

---

## 🆘 Dépannage

### Erreur 403 Forbidden
- Vérifiez que le bucket n'est PAS public
- Vérifiez `AWS_QUERYSTRING_AUTH = True`
- Vérifiez les clés API dans Railway

### Images ne s'affichent pas
- Vérifiez la CSP (Content Security Policy)
- Ajoutez l'endpoint R2 dans `img-src`

### Erreur "No module named 'storages'"
```bash
pip install django-storages[s3] boto3
```

Ajoutez à `requirements.txt` :
```
django-storages[s3]>=1.14
boto3>=1.34
```
