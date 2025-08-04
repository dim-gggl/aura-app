from django.contrib import admin
from .models import Artist, Artwork, ArtworkPhoto, Collection, Exhibition, WishlistItem

class ArtworkPhotoInline(admin.TabularInline):
    model = ArtworkPhoto
    extra = 1

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'nationality', 'birth_year', 'death_year']
    list_filter = ['nationality']
    search_fields = ['name', 'nationality']
    ordering = ['name']

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_artists_display', 'art_type', 'creation_year', 'current_location', 'user']
    list_filter = ['art_type', 'current_location', 'is_signed', 'is_framed', 'user']
    search_fields = ['title', 'artists__name', 'keywords', 'notes']
    filter_horizontal = ['artists', 'collections', 'exhibitions']
    inlines = [ArtworkPhotoInline]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'title', 'artists', 'creation_year', 'origin_country')
        }),
        ('Caractéristiques artistiques', {
            'fields': ('art_type', 'support', 'technique', 'height', 'width', 'depth', 'weight')
        }),
        ('Statut et localisation', {
            'fields': ('current_location', 'is_signed', 'is_framed', 'is_borrowed', 'is_acquired', 'owners')
        }),
        ('Acquisition', {
            'fields': ('acquisition_date', 'acquisition_place', 'price', 'provenance')
        }),
        ('Organisation', {
            'fields': ('collections', 'exhibitions', 'parent_artwork', 'last_exhibited')
        }),
        ('Métadonnées', {
            'fields': ('keywords', 'contextual_references', 'notes', 'id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'description']

@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'start_date', 'end_date', 'user']
    list_filter = ['user', 'start_date']
    search_fields = ['name', 'location', 'description']
    date_hierarchy = 'start_date'

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist_name', 'priority', 'estimated_price', 'user', 'created_at']
    list_filter = ['priority', 'user', 'created_at']
    search_fields = ['title', 'artist_name', 'notes']