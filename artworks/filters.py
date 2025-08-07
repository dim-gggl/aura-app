"""
Django filters for the artworks application.

This module provides filtering capabilities for artwork listings using
django-filter. It allows users to search and filter artworks by various
criteria including artists, types, dates, locations, and characteristics.

The filters integrate with the artwork list view to provide an advanced
search interface that helps users find specific artworks in their collection.
"""

import django_filters
from .models import Artwork, Artist


class ArtworkFilter(django_filters.FilterSet):
    """
    Comprehensive filtering system for artwork listings.
    
    This FilterSet provides multiple ways to search and filter artworks:
    - Text search in titles (case-insensitive, partial matches)
    - Multiple artist selection
    - Various metadata filters (type, support, technique)
    - Date-based filtering (creation, acquisition)
    - Location and status filters
    - Relationship filters (collections, exhibitions)
    
    The filter integrates with Django templates to provide form controls
    and works with pagination to maintain filter state across pages.
    
    Usage:
        In views:
            artwork_filter = ArtworkFilter(request.GET, queryset=artworks)
            filtered_artworks = artwork_filter.qs
        
        In templates:
            {{ filter.form.as_p }}  # Renders all filter fields
            {{ filter.form.title }}  # Individual field access
    """
    
    # Custom title filter with case-insensitive partial matching
    title = django_filters.CharFilter(
        lookup_expr='icontains', 
        label='Titre',
        help_text="Recherche dans les titres des œuvres"
    )
    
    # Multiple artist selection filter
    # Queryset is set dynamically in the view to show only relevant artists
    artists = django_filters.ModelMultipleChoiceFilter(
        queryset=Artist.objects.all(), 
        label='Artiste(s)',
        help_text="Sélectionnez un ou plusieurs artistes"
    )

    class Meta:
        model = Artwork
        fields = [
            # Artist and basic info filters
            'artists',           # Multiple choice - set dynamically in view
            'art_type',         # Select dropdown from ArtType model
            'support',          # Select dropdown from Support model  
            'technique',        # Select dropdown from Technique model
            'creation_year',    # Exact year match
            'origin_country',   # Exact country match
            
            # Acquisition filters
            'acquisition_date', # Exact date match
            'acquisition_place', # Exact place match
            'price',            # Exact price match
            
            # Categorization filters
            'keywords',         # Multiple choice from Keyword model
            'collections',      # Multiple choice - filtered by user in view
            'exhibitions',      # Multiple choice - filtered by user in view
            'parent_artwork',   # Select from user's artworks
            'owners',           # Exact text match
            
            # Status and location filters
            'current_location', # Select from predefined choices
            'is_signed',        # Boolean checkbox
            'is_framed',        # Boolean checkbox
            'is_borrowed',      # Boolean checkbox
            'is_acquired',      # Boolean checkbox
        ]
        
        # Note: Additional filter customization can be added here:
        # - Date range filters for acquisition_date
        # - Price range filters with min/max values
        # - Text search in additional fields (notes, references)
        # - Complex lookups (e.g., creation_year__gte for "after year X")