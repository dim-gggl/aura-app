"""
Core views for the Aura art collection management application.

This module contains the main views that provide the core functionality of the
application, including the homepage, dashboard, and global search functionality.
These views serve as the central hub for users to navigate and get an overview
of their entire collection.

Key features:
- Homepage with authentication redirect logic
- Comprehensive dashboard with statistics and recent activity
- Global search across all user data (artworks, contacts, notes)
- Performance-optimized queries with proper filtering and limiting
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.db import connection

# Import models from related applications
from artworks.models import Artwork, WishlistItem
from contacts.models import Contact
from notes.models import Note


def home(request):
    """
    Homepage view that redirects authenticated users to dashboard.
    
    This view serves as the entry point for the application. It provides
    different experiences for authenticated and anonymous users:
    - Authenticated users are redirected to their personalized dashboard
    - Anonymous users see a welcome page with login/registration options
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Redirect to dashboard or rendered home template
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/home.html')


@login_required
def dashboard(request):
    """
    Main dashboard view providing comprehensive overview of user's collection.
    
    This view serves as the central hub for authenticated users, displaying:
    - Key statistics (counts of artworks, contacts, notes, wishlist items)
    - Recent activity (newest artworks)
    - Data analytics (location distribution, art type breakdown)
    - Personalized suggestions (artworks to exhibit)
    - Quick access to favorite notes
    
    Performance considerations:
    - Uses efficient count() queries for statistics
    - Limits result sets to prevent performance issues
    - Uses select_related/prefetch_related where appropriate
    - Excludes null values in aggregations to avoid skewed data
    
    Args:
        request: HTTP request object (must be from authenticated user)
        
    Returns:
        HttpResponse: Rendered dashboard template with context data
    """
    # === BASIC STATISTICS ===
    # Get counts of all major entities for the current user
    total_artworks = Artwork.objects.filter(user=request.user).count()
    total_contacts = Contact.objects.filter(user=request.user).count()
    total_notes = Note.objects.filter(user=request.user).count()
    total_wishlist = WishlistItem.objects.filter(user=request.user).count()
    
    # === RECENT ACTIVITY ===
    # Get the 5 most recently added artworks for quick access
    recent_artworks = Artwork.objects.filter(
        user=request.user
    ).select_related('art_type').prefetch_related('artists', 'photos').order_by('-created_at')[:5]
    
    # === ANALYTICS DATA ===
    # Artwork distribution by current location
    # Helps users understand where their collection is stored/displayed
    location_stats = Artwork.objects.filter(user=request.user).values(
        'current_location'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Artwork distribution by art type (top 5)
    # Excludes artworks without art_type to avoid null entries in stats
    art_type_stats = Artwork.objects.filter(
        user=request.user
    ).exclude(
        art_type__isnull=True  # Exclude artworks without art type
    ).values('art_type__name').annotate(  # Use art_type__name for readable labels
        count=Count('id')
    ).order_by('-count')[:5]  # Limit to top 5 for dashboard display
    
    # === FAVORITE NOTES ===
    # Get user's favorite notes for quick access
    # Limited to 3 most recently updated for dashboard space efficiency
    favorite_notes = Note.objects.filter(
        user=request.user, 
        is_favorite=True
    ).order_by('-updated_at')[:3]
    
    # === EXHIBITION SUGGESTION ===
    # Suggest an artwork that hasn't been exhibited recently
    # Helps users discover pieces in their collection that could be displayed
    six_months_ago = datetime.now().date() - timedelta(days=180)
    suggested_artwork = Artwork.objects.filter(
        user=request.user,
        # Only consider artworks that are available for exhibition
        current_location__in=['domicile', 'stockage']
    ).filter(
        # Either never exhibited or not exhibited in the last 6 months
        Q(last_exhibited__lt=six_months_ago) | Q(last_exhibited__isnull=True)
    ).select_related('art_type').prefetch_related('artists').first()
    
    # === CONTEXT PREPARATION ===
    context = {
        # Statistics for dashboard widgets
        'total_artworks': total_artworks,
        'total_contacts': total_contacts,
        'total_notes': total_notes,
        'total_wishlist': total_wishlist,
        
        # Recent activity data
        'recent_artworks': recent_artworks,
        
        # Analytics data for charts/visualizations
        'location_stats': location_stats,
        'art_type_stats': art_type_stats,
        
        # Quick access data
        'favorite_notes': favorite_notes,
        'suggested_artwork': suggested_artwork,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def search(request):
    """
    Global search functionality across all user data.
    
    This view provides comprehensive search capabilities across all of the user's
    data including artworks, contacts, and notes. It performs case-insensitive
    partial matching across multiple fields for each entity type.
    
    Search strategy:
    - Uses Q objects for complex OR queries across multiple fields
    - Limits results to prevent performance issues and improve UX
    - Uses distinct() to avoid duplicate results from JOIN operations
    - Searches only user's own data for privacy and performance
    
    Search fields by entity:
    - Artworks: title, artist names, tags, notes
    - Contacts: name, address, notes
    - Notes: title, content
    
    Args:
        request: HTTP request object with optional 'q' GET parameter
        
    Returns:
        HttpResponse: Rendered search results template
    """
    # Get search query from GET parameters
    query = request.GET.get('q', '').strip()
    
    # Initialize empty results structure
    results = {
        'artworks': [],
        'contacts': [],
        'notes': [],
    }
    
    # Only perform search if query is provided
    if query:
        # === ARTWORK SEARCH ===
        # Search across title, artist names, tags, and notes fields
        results['artworks'] = Artwork.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=query) |                    # Title contains query
            Q(artists__name__icontains=query) |            # Artist name contains query
            Q(tags__name__icontains=query) |               # Tag contains query
            Q(notes__icontains=query)                      # Notes contain query
        ).select_related('art_type').prefetch_related(
            'artists', 'photos'
        ).distinct()[:10]  # Limit to 10 results, use distinct() to avoid duplicates from JOINs
        
        # === CONTACT SEARCH ===
        # Search across name, address, and notes fields
        results['contacts'] = Contact.objects.filter(
            user=request.user
        ).filter(
            Q(name__icontains=query) |                     # Name contains query
            Q(address__icontains=query) |                  # Address contains query
            Q(notes__icontains=query)                      # Notes contain query
        )[:10]  # Limit to 10 results
        
        # === NOTE SEARCH ===
        # Search across title and content fields
        results['notes'] = Note.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=query) |                    # Title contains query
            Q(content__icontains=query)                    # Content contains query
        )[:10]  # Limit to 10 results
    
    # === CONTEXT PREPARATION ===
    context = {
        'query': query,
        'results': results,
        # Calculate total results for display
        'total_results': (
            len(results['artworks']) + 
            len(results['contacts']) + 
            len(results['notes'])
        ),
    }
    
    return render(request, 'core/search.html', context)


def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    
    This endpoint provides a simple way to check if the application is running
    and can connect to its database. It's used by Docker health checks,
    load balancers, and monitoring systems.
    
    Returns:
        JsonResponse: Status information with HTTP 200 for healthy, 500 for unhealthy
    """
    try:
        # Test database connection
        connection.ensure_connection()
        
        # Basic application health check
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'database': 'connected'
        }
        
        return JsonResponse(health_status, status=200)
        
    except Exception as e:
        # Return unhealthy status if any error occurs
        health_status = {
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'error': str(e)
        }
        
        return JsonResponse(health_status, status=500)


def site_manifest(request):
    """
    Serve the Web App Manifest with correct hashed static URLs.

    Returns:
        HttpResponse: JSON manifest with content type application/manifest+json
    """
    return render(request, 'site.webmanifest', content_type='application/manifest+json')