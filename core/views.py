# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from datetime import datetime, timedelta

from artworks.models import Artwork, WishlistItem
from contacts.models import Contact
from notes.models import Note

def home(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    # Statistiques de base
    total_artworks = Artwork.objects.filter(user=request.user).count()
    total_contacts = Contact.objects.filter(user=request.user).count()
    total_notes = Note.objects.filter(user=request.user).count()
    total_wishlist = WishlistItem.objects.filter(user=request.user).count()
    
    # Œuvres récentes
    recent_artworks = Artwork.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Œuvres par localisation
    location_stats = Artwork.objects.filter(user=request.user).values('current_location').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Œuvres par type d'art
    # Correction : on doit exclure les œuvres où art_type est nul (None), pas une chaîne vide
    art_type_stats = Artwork.objects.filter(user=request.user).exclude(
        art_type__isnull=True
    ).values('art_type').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Notes favorites
    favorite_notes = Note.objects.filter(user=request.user, is_favorite=True).order_by('-updated_at')[:3]
    
    # Suggestion d'œuvre à exposer
    six_months_ago = datetime.now().date() - timedelta(days=180)
    suggested_artwork = Artwork.objects.filter(
        user=request.user,
        current_location__in=['domicile', 'stockage']
    ).filter(
        Q(last_exhibited__lt=six_months_ago) | Q(last_exhibited__isnull=True)
    ).first()
    
    context = {
        'total_artworks': total_artworks,
        'total_contacts': total_contacts,
        'total_notes': total_notes,
        'total_wishlist': total_wishlist,
        'recent_artworks': recent_artworks,
        'location_stats': location_stats,
        'art_type_stats': art_type_stats,
        'favorite_notes': favorite_notes,
        'suggested_artwork': suggested_artwork,
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def search(request):
    query = request.GET.get('q', '')
    results = {
        'artworks': [],
        'contacts': [],
        'notes': [],
    }
    
    if query:
        # Recherche dans les œuvres
        results['artworks'] = Artwork.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=query) |
            Q(artists__name__icontains=query) |
            Q(keywords__name__icontains=query) |
            Q(notes__icontains=query)
        ).distinct()[:10]
        
        # Recherche dans les contacts
        results['contacts'] = Contact.objects.filter(
            user=request.user
        ).filter(
            Q(name__icontains=query) |
            Q(address__icontains=query) |
            Q(notes__icontains=query)
        )[:10]
        
        # Recherche dans les notes
        results['notes'] = Note.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )[:10]
    
    context = {
        'query': query,
        'results': results,
    }
    
    return render(request, 'core/search.html', context)
