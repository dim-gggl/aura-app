"""
URL configuration for the notes application.

This module defines URL patterns for comprehensive note management,
providing all standard CRUD operations plus additional features like
favorite toggling. The URLs follow RESTful conventions for intuitive
navigation and consistent user experience.

URL Structure:
- / : Note list with search and filtering capabilities
- /create/ : Note creation form
- /<id>/ : Note detail view with full content
- /<id>/edit/ : Note editing form
- /<id>/delete/ : Note deletion confirmation
- /<id>/toggle-favorite/ : Toggle favorite status

All URLs require authentication and enforce user-specific data access.
"""

from django.urls import path

from . import views

# Namespace for the notes app - allows {% url 'notes:list' %} in templates
app_name = "notes"

urlpatterns = [
    # ========================================
    # NOTE MANAGEMENT URLS
    # ========================================
    # Main note list with search and filtering capabilities
    # Supports GET parameters: search, favorites, page
    path("", views.note_list, name="list"),
    # Note creation form
    # POST: Create new note, GET: Display creation form
    path("create/", views.note_create, name="create"),
    # Note detail view - displays full note content and metadata
    # Shows creation/update timestamps, word count, and favorite status
    path("<int:pk>/", views.note_detail, name="detail"),
    # Export endpoints
    path("<int:pk>/export/html/", views.note_export_html, name="export_html"),
    path("<int:pk>/export/pdf/", views.note_export_pdf, name="export_pdf"),
    # Note editing form
    # POST: Update note, GET: Display edit form with current data
    path("<int:pk>/edit/", views.note_update, name="update"),
    # Note deletion with confirmation
    # POST: Confirm deletion, GET: Display confirmation page
    path("<int:pk>/delete/", views.note_delete, name="delete"),
    # ========================================
    # NOTE FEATURE URLS
    # ========================================
    # Toggle favorite status for quick access management
    # Can be used for both regular requests and AJAX calls
    path(
        "<int:pk>/toggle-favorite/", views.note_toggle_favorite, name="toggle_favorite"
    ),
    # Optional: AJAX endpoint for favorite toggling can be added here
]

# URL Pattern Notes:
# - Uses integer primary keys (<int:pk>) for note identification
# - All views require authentication via @login_required decorator
# - User-specific data access is enforced in each view
# - RESTful URL structure for intuitive navigation
# - Consistent naming convention with other apps in the project
# - Additional feature URLs (like favorite toggling) follow semantic naming
