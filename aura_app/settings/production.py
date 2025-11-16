import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from . import base


def _clone_setting(value):
    if isinstance(value, dict):
        return value.copy()
    if isinstance(value, list):
        return list(value)
    if isinstance(value, set):
        return set(value)
    return value


# Bring uppercase settings from base into this module without star imports
for _name in dir(base):
    if _name.isupper():
        globals()[_name] = _clone_setting(getattr(base, _name))

# Explicit aliases for static analysis
BASE_DIR = base.BASE_DIR
INSTALLED_APPS = list(base.INSTALLED_APPS)
MIDDLEWARE = list(base.MIDDLEWARE)
STORAGES = base.STORAGES.copy()


############################################
#                HELPERS
############################################
def get_env(name: str, default=None, required: bool = False):
    val = os.getenv(name, default)
    if required and (val is None or (isinstance(val, str) and val.strip() == "")):
        raise ImproperlyConfigured(f"Missing required environment variable: {name}")
    return val


############################################
#                 CORE
############################################
DEBUG = False

SECRET_KEY = get_env("SECRET_KEY", required=True)

ALLOWED_HOSTS = [h.strip() for h in get_env("ALLOWED_HOSTS", required=True).split(",")]
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in get_env("CSRF_TRUSTED_ORIGINS", required=True).split(",")
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

############################################
#               DATABASE
############################################
DATABASE_URL = get_env("DATABASE_URL", required=True)
DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=False)
}

############################################
#         CACHE (optional Redis)
############################################
REDIS_URL = get_env("REDIS_URL")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "TIMEOUT": 300,
            "KEY_PREFIX": get_env("CACHE_KEY_PREFIX", "aura"),
        }
    }

############################################
#            STATIC / MEDIA
############################################
STATIC_URL = "/static/"
STATIC_ROOT = Path(BASE_DIR) / "staticfiles"

if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    try:
        sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
        MIDDLEWARE.insert(sec_idx + 1, "whitenoise.middleware.WhiteNoiseMiddleware")
    except ValueError:
        MIDDLEWARE.insert(0, "whitenoise.middleware.WhiteNoiseMiddleware")

if "whitenoise.runserver_nostatic" not in INSTALLED_APPS:
    INSTALLED_APPS += ["whitenoise.runserver_nostatic"]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
    "default": (
        {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"}
        if get_env("AWS_STORAGE_BUCKET_NAME")
        and (get_env("AWS_ACCESS_KEY_ID") and get_env("AWS_SECRET_ACCESS_KEY"))
        else {"BACKEND": "django.core.files.storage.FileSystemStorage"}
    ),
}

AWS_S3_ENDPOINT_URL = get_env("AWS_S3_ENDPOINT_URL")
AWS_STORAGE_BUCKET_NAME = get_env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = get_env("AWS_S3_REGION_NAME")
AWS_ACCESS_KEY_ID = get_env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env("AWS_SECRET_ACCESS_KEY")

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

############################################
#           SECURITY HEADERS
############################################
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Cookies
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Clickjacking / MIME sniffing
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# HSTS (1 mois, étends à 6-12 mois quand tout est stable)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Referrer Policy
SECURE_REFERRER_POLICY = "same-origin"

# Cross-Origin Opener Policy (safe par défaut)
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

############################################
#    CONTENT SECURITY POLICY (django-csp)
############################################
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE += ["corsheaders.middleware.CorsMiddleware"]
CORS_ALLOW_CREDENTIALS = (
    True  # Permet aux cookies d'être envoyés avec les requêtes CORS
)

if not "csp" in INSTALLED_APPS:
    INSTALLED_APPS.append("csp")
if "csp.middleware.CSPMiddleware" not in MIDDLEWARE:
    try:
        sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
        MIDDLEWARE.insert(sec_idx + 1, "csp.middleware.CSPMiddleware")
    except ValueError:
        MIDDLEWARE.insert(0, "csp.middleware.CSPMiddleware")

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'", "unsafe-inline"),
        "style-src": (
            "'self'",
            "unsafe-inline",
            "https://cdn.jsdelivr.net",
            "https://fonts.googleapis.com",
        ),
        "script-src": (
            "'self'",
            "https://cdn.jsdelivr.net",
            "unsafe-inline",
        ),
        "object-src": ("none",),
        "img-src": (
            "'self'",
            "data:",
            "blob:",
        ),
        "font-src": (
            "'self'",
            "https://fonts.gstatic.com",
            "data:",
        ),
    }
}

############################################
#           ADMIN HARDENING
############################################
ADMIN_URL = get_env("ADMIN_URL", "admin-locked/")

############################################
#               LOGGING
############################################
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "aura_app": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
