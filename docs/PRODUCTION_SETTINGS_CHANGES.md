# Modifications à apporter à production.py pour R2 privé

## Fichier : `aura_app/settings/production.py`

### Modification 1 : Configuration S3/R2 (lignes 113-122)

**Remplacez :**
```python
if STORAGES["default"]["BACKEND"].endswith("S3Boto3Storage"):
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=31536000, public"}
    if AWS_S3_ENDPOINT_URL and AWS_STORAGE_BUCKET_NAME:
        MEDIA_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/"
    elif AWS_STORAGE_BUCKET_NAME:
        MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = Path(BASE_DIR) / "media"
```

**Par :**
```python
if STORAGES["default"]["BACKEND"].endswith("S3Boto3Storage"):
    # Configuration pour accès PRIVÉ avec URLs signées temporaires
    AWS_DEFAULT_ACL = None  # Pas d'ACL publique
    AWS_QUERYSTRING_AUTH = True  # ← NOUVEAU : Active les URLs signées
    AWS_S3_FILE_OVERWRITE = False  # ← NOUVEAU : Évite l'écrasement

    # ← NOUVEAU : Durée de validité des URLs signées (1 heure)
    AWS_QUERYSTRING_EXPIRE = 3600

    # ← MODIFIÉ : Cache privé au lieu de public
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "private, max-age=3600",  # ← "private" au lieu de "public"
        "ContentDisposition": "inline",  # ← NOUVEAU : Affiche au lieu de télécharger
    }

    # MEDIA_URL (utilisé comme base, mais les URLs seront signées dynamiquement)
    if AWS_S3_ENDPOINT_URL and AWS_STORAGE_BUCKET_NAME:
        MEDIA_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/"
    elif AWS_STORAGE_BUCKET_NAME:
        MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = Path(BASE_DIR) / "media"
```

---

### Modification 2 : CSP pour R2 (lignes 183-188)

**Ajoutez votre endpoint R2 dans la directive `img-src` :**

```python
"img-src": (
    "'self'",
    "data:",
    "blob:",
    "https://<VOTRE-ACCOUNT-ID>.r2.cloudflarestorage.com",  # ← AJOUTEZ CETTE LIGNE
),
```

**Note :** Remplacez `<VOTRE-ACCOUNT-ID>` par votre vrai account ID R2, ou utilisez une variable d'environnement :

```python
"img-src": (
    "'self'",
    "data:",
    "blob:",
    get_env("AWS_S3_ENDPOINT_URL", "").replace("https://", "https://"),  # ← Alternative dynamique
),
```

---

## Résumé des changements

| Paramètre | Avant | Après | Raison |
|-----------|-------|-------|--------|
| `AWS_QUERYSTRING_AUTH` | Non défini | `True` | Active les URLs signées |
| `AWS_QUERYSTRING_EXPIRE` | Non défini | `3600` (1h) | Durée de validité |
| `AWS_S3_FILE_OVERWRITE` | Non défini | `False` | Sécurité |
| `CacheControl` | `public` | `private` | Fichiers privés |
| `ContentDisposition` | Non défini | `inline` | Affichage navigateur |
| CSP `img-src` | Sans R2 | Avec endpoint R2 | Autorise les images |

---

## Après les modifications

1. Commitez les changements
2. Poussez sur Railway
3. Vérifiez les variables d'environnement
4. Testez l'upload d'une image
5. Vérifiez que l'URL générée contient `?AWSAccessKeyId=...&Signature=...`
