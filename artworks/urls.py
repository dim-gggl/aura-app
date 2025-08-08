"""
URL configuration for the artworks application.

This module defines all URL patterns for the artworks app, organized into
logical sections for better maintainability. The URLs support both regular
web views and AJAX endpoints for dynamic functionality.

URL Structure:
- Artwork CRUD: /, create/, <uuid:pk>/, <uuid:pk>/edit/, <uuid:pk>/delete/
- Artist management: artists/*, artists/<int:pk>/*
- Collection management: collections/*, collections/<int:pk>/*
- Exhibition management: exhibitions/*, exhibitions/<int:pk>/*
- Reference entities: art-types/*, supports/*, techniques/*, keywords/*
- AJAX endpoints: ajax/*/create/, ajax/keyword/autocomplete/
- Special features: suggestion/, wishlist/*, export/*

Note: Artworks use UUID primary keys for better security and scalability,
while other entities use standard integer primary keys.
"""

from django.urls import path
from . import views

# Namespace for the artworks app - allows {% url 'artworks:list' %} in templates
app_name = "artworks"

urlpatterns = [
    # ========================================
    # ARTWORK URLS (Main Entity)
    # ========================================
    path("", views.artwork_list, name="list"),  # Main artwork listing page
    path("create/", views.artwork_create, name="create"),
    path("<uuid:pk>/", views.artwork_detail, name="detail"),  # UUID for security
    path("<uuid:pk>/edit/", views.artwork_update, name="update"),
    path("<uuid:pk>/delete/", views.artwork_delete, name="delete"),
    
    # Export functionality
    path("<uuid:pk>/export/html/", views.artwork_export_html, name="export_html"),
    path("<uuid:pk>/export/pdf/", views.artwork_export_pdf, name="export_pdf"),
    # Exports for other entities
    path("artists/<int:pk>/export/html/", views.artist_export_html, name="artist_export_html"),
    path("artists/<int:pk>/export/pdf/", views.artist_export_pdf, name="artist_export_pdf"),
    path("collections/<int:pk>/export/html/", views.collection_export_html, name="collection_export_html"),
    path("collections/<int:pk>/export/pdf/", views.collection_export_pdf, name="collection_export_pdf"),
    path("exhibitions/<int:pk>/export/html/", views.exhibition_export_html, name="exhibition_export_html"),
    path("exhibitions/<int:pk>/export/pdf/", views.exhibition_export_pdf, name="exhibition_export_pdf"),
    
    # Special features
    path("suggestion/", views.random_suggestion, name="random_suggestion"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/<int:pk>/delete/", views.wishlist_delete, name="wishlist_delete"),
    
    # ========================================
    # ARTIST MANAGEMENT URLS
    # ========================================
    path("artists/", views.artist_list, name="artist_list"),
    path("artists/create/", views.artist_create, name="artist_create"),
    path("artists/<int:pk>/", views.artist_detail, name="artist_detail"),
    path("artists/<int:pk>/edit/", views.artist_update, name="artist_update"),
    
    # ========================================
    # COLLECTION MANAGEMENT URLS
    # ========================================
    path("collections/", views.collection_list, name="collection_list"),
    path("collections/create/", views.collection_create, name="collection_create"),
    path("collections/<int:pk>/", views.collection_detail, name="collection_detail"),
    path("collections/<int:pk>/edit/", views.collection_update, name="collection_update"),
    
    # ========================================
    # EXHIBITION MANAGEMENT URLS
    # ========================================
    path("exhibitions/", views.exhibition_list, name="exhibition_list"),
    path("exhibitions/create/", views.exhibition_create, name="exhibition_create"),
    path("exhibitions/<int:pk>/", views.exhibition_detail, name="exhibition_detail"),
    path("exhibitions/<int:pk>/edit/", views.exhibition_update, name="exhibition_update"),
    
    # ========================================
    # REFERENCE ENTITY URLS
    # ========================================
    # These entities are shared across users and provide standardized categorization
    
    # Art Types (painting, sculpture, photography, etc.)
    path("art-types/", views.arttype_list, name="arttype_list"),
    path("art-types/create/", views.arttype_create, name="arttype_create"),
    path("art-types/<int:pk>/edit/", views.arttype_update, name="arttype_update"),
    path("art-types/<int:pk>/delete/", views.arttype_delete, name="arttype_delete"),
    
    # Supports (canvas, paper, wood, etc.)
    path("supports/", views.support_list, name="support_list"),
    path("supports/create/", views.support_create, name="support_create"),
    path("supports/<int:pk>/edit/", views.support_update, name="support_update"),
    path("supports/<int:pk>/delete/", views.support_delete, name="support_delete"),
    
    # Techniques (oil, watercolor, acrylic, etc.)
    path("techniques/", views.technique_list, name="technique_list"),
    path("techniques/create/", views.technique_create, name="technique_create"),
    path("techniques/<int:pk>/edit/", views.technique_update, name="technique_update"),
    path("techniques/<int:pk>/delete/", views.technique_delete, name="technique_delete"),

    
    # ========================================
    # AJAX ENDPOINTS
    # ========================================
    # These endpoints support dynamic form functionality, allowing users to create
    # new entities on-the-fly without page reloads (used by SelectOrCreateWidget)
    
    path("ajax/artist/create/", views.artist_create_ajax, name="artist_create_ajax"),
    path("ajax/collection/create/", views.collection_create_ajax, name="collection_create_ajax"),
    path("ajax/exhibition/create/", views.exhibition_create_ajax, name="exhibition_create_ajax"),
    path("ajax/arttype/create/", views.arttype_create_ajax, name="arttype_create_ajax"),
    path("ajax/support/create/", views.support_create_ajax, name="support_create_ajax"),
    path("ajax/technique/create/", views.technique_create_ajax, name="technique_create_ajax")
]