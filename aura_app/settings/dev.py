from .base import *  # noqa

DEBUG = True

# Security
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "app.local",
    "192.168.1.41",
    "192.168.1.42",
    "192.168.1.43",
    "192.168.1.44",
    "192.168.1.45",
    "192.168.1.46",
    "192.168.1.47",
    "192.168.1.48",
    "192.168.1.49",
]

# Trusted origins for CSRF while developing locally. Django accepts POST
# requests originating from these domains without raising CSRF errors. Make
# sure to restrict the list to production domains before deploying.
CSRF_TRUSTED_ORIGINS = [
    "http://app.local",  # Custom local domain (for example via /etc/hosts)
    "http://localhost:8000",  # Localhost on Django's default port
    "http://127.0.0.1:8000",  # Loopback IP on the default Django port
    "http://192.168.1.41:8000",
    "http://192.168.1.42:8000",
    "http://192.168.1.43:8000",
    "http://192.168.1.44:8000",
    "http://192.168.1.45:8000",
    "http://192.168.1.46:8000",
    "http://192.168.1.47:8000",
    "http://192.168.1.48:8000",
    "http://192.168.1.49:8000",
]

# En environnement de développement, il est important de désactiver
# certaines sécurités liées au HTTPS pour faciliter les tests locaux,
# car le serveur de développement Django ne gère pas le SSL/TLS.
SECURE_SSL_REDIRECT = False  # Ne pas forcer la redirection vers HTTPS en local

# Les cookies de session et CSRF ne sont pas marqués comme "secure" pour permettre
# leur transmission en HTTP.
SESSION_COOKIE_SECURE = (
    False  # Le cookie de session peut être transmis en HTTP (non sécurisé)
)
CSRF_COOKIE_SECURE = False  # Le cookie CSRF peut être transmis en HTTP (non sécurisé)

# Pour le développement, les emails sont affichés dans la console au lieu
# d'être envoyés réellement.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache local (file-based par défaut); passez à Redis si dispo
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "aura-dev",
    }
}

# CSP (nouveau format django-csp >= 4) en mode rapport uniquement
CONTENT_SECURITY_POLICY_REPORT_ONLY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "style-src": ("'self'", "'unsafe-inline'"),
        "script-src": ("'self'",),
        "img-src": ("'self'", "data:"),
        "object-src": ("'none'",),
    }
}

# En dev, servir à la racine pour éviter les soucis de cookie CSRF lié au sous-chemin
# (utilisez un proxy externe pour tester un sous-chemin si nécessaire)
# FORCE_SCRIPT_NAME = "/aura"
# USE_X_FORWARDED_HOST = True
# STATIC_URL = "/aura/static/"
# MEDIA_URL = "/aura/media/"
