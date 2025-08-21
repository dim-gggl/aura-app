from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import RedirectView
from django.templatetags.static import static as static_url


# ========================================
# MAIN URL PATTERNS
# ========================================

urlpatterns = [
    # ========================================
    # ADMIN INTERFACE
    # ========================================
    # Django admin interface for site administration
    # Accessible only to staff/superuser accounts
    path(getattr(settings, "ADMIN_URL", "admin/"), admin.site.urls),
    
    # ========================================
    # APPLICATION URL INCLUDES
    # ========================================
    
    # Core application URLs (homepage, dashboard, search)
    # Mounted at root level for primary navigation
    path("", include("core.urls")),
    
    # Artwork collection management
    # Includes CRUD operations, filtering, export, and AJAX endpoints
    path("artworks/", include("artworks.urls")),
    
    # Professional contact management
    # Includes contact CRUD operations with search and filtering
    path("contacts/", include("contacts.urls")),
    
    # Personal note-taking system
    # Includes note CRUD operations with favorites and search
    path("notes/", include("notes.urls")),
    
    # User authentication and account management
    # Includes registration, login, logout, profile, and password management
    path("accounts/", include("accounts.urls")),

    # =========================================
    # API URLS
    # =========================================

    # API Endpoints
    path("api/", include("aura_app.api_urls")),

    # JWT authentication
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

# Root-level redirects for common icon endpoints
urlpatterns += [
    path("favicon.ico", RedirectView.as_view(url=static_url("flavicon/favicon.ico"), permanent=True)),
    path("favicon.svg", RedirectView.as_view(url=static_url("flavicon/favicon.svg"), permanent=True)),
    path("apple-touch-icon.png", RedirectView.as_view(url=static_url("flavicon/apple-touch-icon.png"), permanent=True)),
]

# ========================================
# DEVELOPMENT MEDIA FILE SERVING
# ========================================

# Serve media files during development
# In production, media files are served by the web server or cloud storage (AWS S3)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,           # URL prefix for media files
        document_root=settings.MEDIA_ROOT  # Local directory containing media files
    )

# ========================================
# URL PATTERN NOTES
# ========================================

# URL Hierarchy:
# The URL structure follows a logical hierarchy that matches the application
# architecture and provides intuitive navigation for users:
#
# 1. Core functionality at root level (/, /dashboard/, /search/)
# 2. Main features under descriptive prefixes (/artworks/, /contacts/, /notes/)
# 3. User management under /accounts/ prefix
# 4. Admin functionality under /admin/ prefix
#
# Each application maintains its own URL namespace to avoid conflicts and
# provide clean separation of concerns. This structure supports:
# - RESTful URL design
# - Easy maintenance and debugging
# - Clear application boundaries
# - Scalable URL architecture for future features

# Security Considerations:
# - Admin URLs are kept at /admin/ (consider changing in production)
# - All user-facing URLs require authentication at the view level
# - Media file serving is disabled in production for security
# - URL patterns follow Django security best practices

# Performance Considerations:
# - URL patterns are ordered by frequency of access
# - Static URL includes are used for better performance
# - Media files are served efficiently in development
# - Production deployment uses web server for static/media files