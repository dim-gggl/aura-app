"""
Django settings for the Aura art collection management application.

This module contains all configuration settings for the Django project,
including database configuration, static files, media handling, third-party
app integration, and environment-specific settings.

Key features:
- Environment-based configuration using django-environ
- Adaptive database configuration (SQLite for development, PostgreSQL for production)
- AWS S3 integration for production media storage
- Comprehensive security and authentication settings
- Multi-language and timezone support
- Third-party package integration (Crispy Forms, ImageKit, etc.)

Environment Variables Required:
- SECRET_KEY: Django secret key for cryptographic signing
- DEBUG: Boolean flag for debug mode
- DB_* variables: Database connection parameters (production only)
- AWS_* variables: AWS S3 configuration (production only)
- EMAIL_* variables: SMTP email configuration
"""

import environ
import os
from pathlib import Path

# ========================================
# ENVIRONMENT CONFIGURATION
# ========================================

# Initialize django-environ for environment variable management
# Provides type casting and default values for environment variables
env = environ.Env(
    DEBUG=(bool, False)  # DEBUG defaults to False for security
)

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# Read environment variables from .env file
# This allows for local configuration without committing sensitive data
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# ========================================
# CORE DJANGO SETTINGS
# ========================================

# SECURITY WARNING: keep the secret key used in production secret!
# Uses environment variable with fallback for development
SECRET_KEY = env("SECRET_KEY", default="your-secret-key-here")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

# Hosts/domain names that this Django site can serve
# Includes common development addresses and specific network configurations
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "192.168.1.41", "0.0.0.0"]

# ========================================
# APPLICATION DEFINITION
# ========================================

INSTALLED_APPS = [
    # Django built-in applications
    "django.contrib.admin",          # Admin interface
    "django.contrib.auth",           # Authentication framework
    "django.contrib.contenttypes",   # Content type framework
    "django.contrib.sessions",       # Session framework
    "django.contrib.messages",       # Messaging framework
    "django.contrib.staticfiles",    # Static file management
    "django.contrib.humanize",       # Human-friendly data formatting
    
    # Third-party applications
    "crispy_forms",                   # Enhanced form rendering
    "crispy_bootstrap5",              # Bootstrap 5 support for crispy forms
    "storages",                       # Custom storage backends (AWS S3)
    "imagekit",                       # Image processing and thumbnails
    "django_filters",                 # Advanced filtering for querysets
    
    # Local applications (order matters for template/static file resolution)
    "core",                          # Core functionality and user management
    "artworks",                      # Artwork collection management
    "contacts",                      # Professional contact management
    "notes",                         # Personal note-taking system
    "accounts",                      # User account management
]

# ========================================
# MIDDLEWARE CONFIGURATION
# ========================================

MIDDLEWARE = [
    # Security middleware (must be first)
    "django.middleware.security.SecurityMiddleware",
    
    # WhiteNoise for static file serving in production
    "whitenoise.middleware.WhiteNoiseMiddleware",
    
    # Session management
    "django.contrib.sessions.middleware.SessionMiddleware",
    
    # Common HTTP handling
    "django.middleware.common.CommonMiddleware",
    
    # CSRF protection
    "django.middleware.csrf.CsrfViewMiddleware",
    
    # User authentication
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    
    # Message framework
    "django.contrib.messages.middleware.MessageMiddleware",
    
    # Clickjacking protection
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Root URL configuration module
ROOT_URLCONF = "aura_app.urls"

# ========================================
# TEMPLATE CONFIGURATION
# ========================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Global template directory
        "APP_DIRS": True,  # Look for templates in app directories
        "OPTIONS": {
            "context_processors": [
                # Django built-in context processors
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                
                # Custom context processors
                "core.context_processors.theme_context",  # Theme management
            ],
        },
    },
]

# WSGI application for deployment
WSGI_APPLICATION = "aura_app.wsgi.application"

# ========================================
# DATABASE CONFIGURATION
# ========================================

# Adaptive database configuration based on environment
if DEBUG:
    # SQLite for development - simple, no setup required
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # PostgreSQL for production - robust, scalable
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT", default="5432"),
        }
    }

# ========================================
# PASSWORD VALIDATION
# ========================================

# Password validation rules for user security
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ========================================
# INTERNATIONALIZATION
# ========================================

# Language and timezone configuration
LANGUAGE_CODE = "fr-fr"      # French language
TIME_ZONE = "Europe/Paris"   # Paris timezone
USE_I18N = True              # Enable internationalization
USE_TZ = True                # Enable timezone support

# ========================================
# STATIC FILES CONFIGURATION
# ========================================

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"                    # URL prefix for static files
STATICFILES_DIRS = [BASE_DIR / "static"]   # Additional static file directories
STATIC_ROOT = BASE_DIR / "staticfiles"     # Directory for collected static files

# ========================================
# MEDIA FILES CONFIGURATION
# ========================================

# Media files configuration - adaptive based on environment
if not DEBUG:
    # Production: AWS S3 for scalable media storage
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="eu-west-3")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_DEFAULT_ACL = None  # Use bucket's default ACL
    
    # Optimize file caching
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",  # 24 hours cache
    }
    
    # Use S3 for media file storage
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    # Development: Local file storage
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# ========================================
# THIRD-PARTY PACKAGE CONFIGURATION
# ========================================

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Crispy Forms configuration for Bootstrap 5 styling
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ========================================
# AUTHENTICATION CONFIGURATION
# ========================================

# Custom user model
AUTH_USER_MODEL = "core.User"

# Authentication URLs and redirects
LOGIN_URL = "accounts:login"              # Where to redirect for login
LOGIN_REDIRECT_URL = "core:dashboard"     # Where to redirect after login
LOGOUT_REDIRECT_URL = "core:home"         # Where to redirect after logout

# ========================================
# EMAIL CONFIGURATION
# ========================================

# Email configuration for password reset and notifications
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env("EMAIL_PORT", default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

# ========================================
# SESSION CONFIGURATION
# ========================================

# Security: Sessions expire when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# ========================================
# LOCALIZATION SETTINGS
# ========================================

# Start week on Monday (European standard)
FIRST_DAY_OF_WEEK = 1

# ========================================
# ADDITIONAL SECURITY SETTINGS (for production)
# ========================================

# Uncomment and configure these for production deployment:
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True
# X_FRAME_OPTIONS = 'DENY'
# SECURE_REFERRER_POLICY = 'same-origin'