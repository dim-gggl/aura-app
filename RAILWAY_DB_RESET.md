# Railway Database Reset - Solution complète

## Le Problème

Django ne détecte pas les apps locales (`core`, `accounts`, `artworks`, etc.) lors des migrations sur Railway, même après avoir corrigé les settings. Les logs montrent:

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, taggit, token_blacklist
```

**Manquent**: `core`, `accounts`, `artworks`, `contacts`, `notes`

## Cause Racine

La base de données Railway a déjà des migrations partiellement appliquées avec les **mauvais settings**. La table `django_migrations` contient un état incohérent qui bloque les nouvelles migrations.

## Solution: Réinitialiser la Base de Données

### Option 1: Via l'Interface Railway (Recommandé)

1. **Allez dans votre projet Railway**
2. **Cliquez sur le service PostgreSQL**
3. **Onglet "Data"**
4. **"Reset Database"** ou supprimez toutes les tables manuellement
5. **Redéployez l'application** - les migrations s'exécuteront correctement

### Option 2: Via Script (Avancé)

Si vous avez accès à l'URL de la base de données:

1. **Récupérez DATABASE_URL depuis Railway**:
   - Dashboard → PostgreSQL service → Variables → DATABASE_URL

2. **Exécutez le script de reset**:
   ```bash
   export DATABASE_URL='postgresql://user:pass@host:port/db'
   ./reset_railway_db.sh
   ```

3. **Redéployez sur Railway**:
   ```bash
   git push origin main
   ```

### Option 3: Supprimer et Recréer le Service PostgreSQL

1. **Sauvegardez vos données si nécessaire** (export SQL)
2. **Supprimez le service PostgreSQL** dans Railway
3. **Créez un nouveau service PostgreSQL**
4. **Mettez à jour la variable DATABASE_URL** dans votre service web
5. **Redéployez**

## Vérification Post-Reset

Après le redéploiement, les logs devraient montrer:

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, accounts, artworks, contacts, notes, sessions, taggit, token_blacklist
Running migrations:
  Applying core.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying accounts.0001_initial... OK
  Applying artworks.0001_initial... OK
  ...
```

✅ Notez la présence de **core**, **accounts**, **artworks**, **contacts**, **notes**

## Pourquoi Cette Solution Fonctionne

1. **Fixes déjà appliqués** (dans les commits précédents):
   - `core` app avant `django.contrib.admin` dans INSTALLED_APPS
   - Settings production par défaut dans wsgi.py, asgi.py, settings/__init__.py

2. **Le reset permet**:
   - Effacer l'état de migration corrompu
   - Repartir de zéro avec les bons settings
   - Créer toutes les tables dans le bon ordre

## Prévention Future

- ✅ Ne jamais lancer `manage.py migrate` localement avec des settings qui pointent vers la DB de production
- ✅ Toujours vérifier que `DJANGO_SETTINGS_MODULE` est correctement défini
- ✅ Utiliser `.env.dev.example` pour le développement local

## Besoin d'Aide?

Si le reset ne résout pas le problème:

1. Vérifiez que Railway utilise bien le dernier commit
2. Consultez les logs complets de déploiement
3. Vérifiez que toutes les variables d'environnement sont définies sur Railway
