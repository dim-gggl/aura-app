# Development Setup

## Quick Start for Local Development

Since the project now defaults to **production settings**, you need to explicitly set the development environment for local work.

### Option 1: Using .env file (Recommended)

1. Copy the development environment template:
   ```bash
   cp .env.dev.example .env
   ```

2. The `.env` file already sets `DJANGO_SETTINGS_MODULE=aura_app.settings.dev`

3. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Option 2: Set environment variable manually

```bash
export DJANGO_SETTINGS_MODULE=aura_app.settings.dev
python manage.py runserver
```

### Option 3: Use manage.py with explicit settings

```bash
python manage.py runserver --settings=aura_app.settings.dev
```

## Why This Change?

Previously, the project defaulted to development settings, which caused deployment issues on Railway. Now:

- **Production environments** (Railway, Docker, etc.) automatically use `aura_app.settings.production`
- **Local development** requires explicitly setting `DJANGO_SETTINGS_MODULE=aura_app.settings.dev`

This ensures:
- ✅ Deployments work correctly without manual configuration
- ✅ All Django apps (core, accounts, artworks, etc.) are properly detected
- ✅ Migrations run in the correct order
- ✅ Production security settings are enabled by default

## Production Deployment

For Railway or other platforms, ensure these environment variables are set:

```
DJANGO_SETTINGS_MODULE=aura_app.settings.production
DATABASE_URL=postgresql://...
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

See `.env.production.example` for the complete list of required variables.
