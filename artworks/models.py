from django.db import models
# from django.contrib.auth.models import User
from django.urls import reverse
import uuid
from core.models import User


class Artist(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")
    birth_year = models.IntegerField(null=True, blank=True, verbose_name="Année de naissance")
    death_year = models.IntegerField(null=True, blank=True, verbose_name="Année de décès")
    nationality = models.CharField(max_length=100, blank=True, verbose_name="Nationalité")
    biography = models.TextField(blank=True, verbose_name="Biographie")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Artiste"
        verbose_name_plural = "Artistes"
    
    def __str__(self):
        return self.name


class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=200, verbose_name="Nom de la collection")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Collection"
        verbose_name_plural = "Collections"
    
    def __str__(self):
        return self.name


class Exhibition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exhibitions')
    name = models.CharField(max_length=200, verbose_name="Nom de l'exposition")
    location = models.CharField(max_length=200, blank=True, verbose_name="Lieu")
    start_date = models.DateField(null=True, blank=True, verbose_name="Date de début")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Exposition"
        verbose_name_plural = "Expositions"
    
    def __str__(self):
        return self.name


class ArtType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Type d'art")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Type d'art"
        verbose_name_plural = "Types d'art"
    
    def __str__(self):
        return self.name


class Support(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Support")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Support"
        verbose_name_plural = "Supports"
    
    def __str__(self):
        return self.name


class Technique(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Technique")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Technique"
        verbose_name_plural = "Techniques"
    
    def __str__(self):
        return self.name


class Keyword(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Mot-clé")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Mot-clé"
        verbose_name_plural = "Mots-clés"
    
    def __str__(self):
        return self.name


class Artwork(models.Model):
    ART_TYPES = [
        ('peinture', 'Peinture'),
        ('sculpture', 'Sculpture'),
        ('photographie', 'Photographie'),
        ('gravure', 'Gravure'),
        ('dessin', 'Dessin'),
        ('bd', 'Bande dessinée'),
        ('illustration', 'Illustration'),
        ('poésie', 'Poésie'),
        ('autre', 'Autre'),
    ]
    
    LOCATIONS = [
        ('domicile', 'Domicile'),
        ('stockage', 'Stockage'),
        ('exposee', 'Exposée'),
        ('pretee', 'Prêtée'),
        ('restauration', 'En restauration'),
        ('autre', 'Autre'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artworks')
    
    # Informations de base
    title = models.CharField(max_length=300, blank=True, verbose_name="Titre")
    artists = models.ManyToManyField(Artist, blank=True, verbose_name="Artiste(s)")
    creation_year = models.IntegerField(null=True, blank=True, verbose_name="Année de création")
    origin_country = models.CharField(max_length=100, blank=True, verbose_name="Pays d'origine")
    art_type = models.ForeignKey(ArtType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Type d'art")
    support = models.ForeignKey(Support, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Support")
    technique = models.ForeignKey(Technique, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Technique")
    
    # Dimensions et poids
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Hauteur (cm)")
    width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Largeur (cm)")
    depth = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Profondeur (cm)")
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Poids (kg)")
    
    # Acquisition
    acquisition_date = models.DateField(null=True, blank=True, verbose_name="Date d'acquisition")
    acquisition_place = models.CharField(max_length=200, blank=True, verbose_name="Lieu d'acquisition")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix (€)")
    provenance = models.TextField(blank=True, verbose_name="Provenance")
    
    # Statut et localisation
    is_framed = models.BooleanField(default=False, verbose_name="Est encadrée")
    is_borrowed = models.BooleanField(default=False, verbose_name="Est empruntée")
    is_signed = models.BooleanField(default=False, verbose_name="Est signée")
    is_acquired = models.BooleanField(default=True, verbose_name="Est acquise")
    current_location = models.CharField(max_length=50, choices=LOCATIONS, default='domicile', verbose_name="Localisation actuelle")
    
    # Relations
    collections = models.ManyToManyField(Collection, blank=True, verbose_name="Collection(s)")
    exhibitions = models.ManyToManyField(Exhibition, blank=True, verbose_name="Exposition(s)")
    parent_artwork = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Œuvre parente")
    owners = models.CharField(max_length=500, blank=True, verbose_name="Propriétaire(s)")
    
    # Informations complémentaires
    keywords = models.ManyToManyField(Keyword, blank=True, verbose_name="Mots-clés")
    contextual_references = models.TextField(blank=True, verbose_name="Références contextuelles")
    notes = models.TextField(blank=True, verbose_name="Notes libres")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_exhibited = models.DateField(null=True, blank=True, verbose_name="Dernière exposition")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Œuvre d'art"
        verbose_name_plural = "Œuvres d'art"
    
    def __str__(self):
        if self.title:
            return self.title
        elif self.artists.exists():
            return f"Œuvre de {', '.join([artist.name for artist in self.artists.all()])}"
        else:
            return f"Œuvre #{str(self.id)[:8]}"
    
    def get_absolute_url(self):
        return reverse('artworks:detail', kwargs={'pk': self.pk})
    
    def get_artists_display(self):
        return ', '.join([artist.name for artist in self.artists.all()])
    
    def get_dimensions_display(self):
        dimensions = []
        if self.height:
            dimensions.append(f"H: {self.height}cm")
        if self.width:
            dimensions.append(f"L: {self.width}cm")
        if self.depth:
            dimensions.append(f"P: {self.depth}cm")
        return ' × '.join(dimensions) if dimensions else "Non spécifiées"


class ArtworkPhoto(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='artworks/photos/%Y/%m/%d/', verbose_name="Photo")
    caption = models.CharField(max_length=300, blank=True, verbose_name="Légende")
    is_primary = models.BooleanField(default=False, verbose_name="Photo principale")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
        verbose_name = "Photo d'œuvre"
        verbose_name_plural = "Photos d'œuvres"
    
    def __str__(self):
        return f"Photo de {self.artwork}"


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    title = models.CharField(max_length=300, verbose_name="Titre")
    artist_name = models.CharField(max_length=200, blank=True, verbose_name="Artiste")
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix estimé (€)")
    priority = models.IntegerField(default=3, choices=[(1, 'Haute'), (2, 'Moyenne'), (3, 'Basse')], verbose_name="Priorité")
    notes = models.TextField(blank=True, verbose_name="Notes")
    source_url = models.URLField(blank=True, verbose_name="URL source")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['priority', '-created_at']
        verbose_name = "Œuvre convoitée"
        verbose_name_plural = "Œuvres convoitées"
    
    def __str__(self):
        return self.title