import os

# Use production settings by default for deployment environments
# Local development should override with DJANGO_SETTINGS_MODULE=aura_app.settings.dev
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aura_app.settings.production")
