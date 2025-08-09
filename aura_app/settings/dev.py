from .base import *  # noqa

DEBUG = True

# Security
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "192.168.1.41"]
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
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