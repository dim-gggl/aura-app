"""
URL configuration for the contacts application.

This module defines URL patterns for comprehensive contact management,
providing all standard CRUD operations with a clean and logical URL structure.
The URLs follow RESTful conventions for intuitive navigation.

URL Structure:
- / : Contact list with search and filtering
- /create/ : Contact creation form
- /<id>/ : Contact detail view
- /<id>/edit/ : Contact editing form
- /<id>/delete/ : Contact deletion confirmation

All URLs require authentication and enforce user-specific data access.
"""

from django.urls import path
from . import views

# Namespace for the contacts app - allows {% url 'contacts:list' %} in templates
app_name = 'contacts'

urlpatterns = [
    # ========================================
    # CONTACT MANAGEMENT URLS
    # ========================================
    
    # Main contact list with search and filtering capabilities
    # Supports GET parameters: search, type, page
    path('', views.contact_list, name='list'),
    
    # Contact creation form
    # POST: Create new contact, GET: Display creation form
    path('create/', views.contact_create, name='create'),
    
    # Contact detail view - comprehensive contact information display
    # Shows all contact fields and metadata
    path('<int:pk>/', views.contact_detail, name='detail'),
    
    # Contact editing form
    # POST: Update contact, GET: Display edit form with current data
    path('<int:pk>/edit/', views.contact_update, name='update'),
    
    # Contact deletion with confirmation
    # POST: Confirm deletion, GET: Display confirmation page
    path('<int:pk>/delete/', views.contact_delete, name='delete'),
]

# URL Pattern Notes:
# - Uses integer primary keys (<int:pk>) for contact identification
# - All views require authentication via @login_required decorator
# - User-specific data access is enforced in each view
# - RESTful URL structure for intuitive API-like navigation
# - Consistent naming convention with other apps in the project