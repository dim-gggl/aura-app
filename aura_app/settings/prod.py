from .base import *  # noqa
DEBUG = False
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

if env("DATABASE_URL") and os.getenv("REDIS_URL"):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.getenv("REDIS_URL"),
        }
    }

CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")