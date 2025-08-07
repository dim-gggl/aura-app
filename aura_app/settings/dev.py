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