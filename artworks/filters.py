# artworks/filters.py
import django_filters
from .models import Artwork, Artist

class ArtworkFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Titre')
    artists = django_filters.ModelMultipleChoiceFilter(queryset=Artist.objects.all(), label='Artiste(s)')

    class Meta:
        model = Artwork
        fields = [
            'artists',
            'art_type', 
            'support',
            'technique',
            'creation_year',
            'origin_country',
            'acquisition_date',
            'acquisition_place',
            'price',
            'keywords',
            'collections',
            'exhibitions',
            'parent_artwork',
            'owners',   
            'current_location', 
            'is_signed', 
            'is_framed',
            'is_borrowed',
            'is_acquired',
            
        ]