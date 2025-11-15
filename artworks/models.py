"""
Django models for the artworks application.

This module contains all the database models related to artwork management,
including artists, artworks, collections, exhibitions, and related entities.
"""

import uuid

from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFit, Transpose
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, Tag

from core.models import User

LOCATIONS = [
    ("domicile", "Domicile"),
    ("stockage", "Stockage"),
    ("pretee", "Prêtée"),
    ("restauration", "En restauration"),
    ("encadrement", "En encadrement"),
    ("restitution", "En restitution"),
    ("vente", "En vente"),
    ("vendue", "Vendue"),
    ("perdue", "Perdue"),
    ("volée", "Volée"),
    ("volée", "Volée"),
    ("autre", "Autre"),
]


class Artist(models.Model):
    """
    Model representing an artist.

    Artists can be associated with multiple artworks and contain biographical
    information such as birth/death years, nationality, and biography.
    """

    # Propriétaire de l'artiste (optionnel pour compatibilité rétro)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="artists",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200, verbose_name="Nom")
    birth_year = models.IntegerField(
        null=True, blank=True, verbose_name="Année de naissance"
    )
    death_year = models.IntegerField(
        null=True, blank=True, verbose_name="Année de décès"
    )
    nationality = models.CharField(
        max_length=100, blank=True, verbose_name="Nationalité"
    )
    biography = models.TextField(blank=True, verbose_name="Biographie")

    # Timestamps for tracking record creation and updates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]  # Order artists alphabetically by name
        verbose_name = "Artiste"
        verbose_name_plural = "Artistes"

    def __str__(self):
        """Return the artist's name as string representation."""
        return self.name


class Collection(models.Model):
    """
    Model representing a user's artwork collection.

    Collections are user-specific groupings of artworks that help organize
    and categorize the user's art collection.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    name = models.CharField(max_length=200, verbose_name="Nom de la collection")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]  # Order collections alphabetically
        verbose_name = "Collection"
        verbose_name_plural = "Collections"

    def __str__(self):
        """Return the collection's name as string representation."""
        return self.name


class Exhibition(models.Model):
    """
    Model representing an exhibition where artworks can be displayed.

    Exhibitions are user-specific events with optional dates, locations,
    and descriptions. Artworks can be associated with multiple exhibitions.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exhibitions")
    name = models.CharField(max_length=200, verbose_name="Nom de l'exposition")
    location = models.CharField(max_length=200, blank=True, verbose_name="Lieu")
    start_date = models.DateField(null=True, blank=True, verbose_name="Date de début")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]  # Order by start date, most recent first
        verbose_name = "Exposition"
        verbose_name_plural = "Expositions"

    def __str__(self):
        """Return the exhibition's name as string representation."""
        return self.name


class ArtType(models.Model):
    """
    Model representing different types of art (painting, sculpture, etc.).

    This is a reference model that provides standardized art type categories
    for artworks. Art types are unique and shared across all users.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name="Type d'art")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]  # Order art types alphabetically
        verbose_name = "Type d'art"
        verbose_name_plural = "Types d'art"

    def __str__(self):
        """Return the art type name as string representation."""
        return self.name


class Support(models.Model):
    """
    Model representing different artwork supports (canvas, paper, wood, etc.).

    This is a reference model that provides standardized support categories
    for artworks. Supports are unique and shared across all users.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name="Support")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]  # Order supports alphabetically
        verbose_name = "Support"
        verbose_name_plural = "Supports"

    def __str__(self):
        """Return the support name as string representation."""
        return self.name


class Technique(models.Model):
    """
    Model representing different artwork techniques (oil, watercolor, etc.).

    This is a reference model that provides standardized technique categories
    for artworks. Techniques are unique and shared across all users.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name="Technique")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]  # Order techniques alphabetically
        verbose_name = "Technique"
        verbose_name_plural = "Techniques"

    def __str__(self):
        """Return the technique name as string representation."""
        return self.name


class Artwork(models.Model):
    """
    Model representing an artwork in a user's collection.

    This is the main model that stores comprehensive information about artworks
    including basic details, dimensions, acquisition info, status, and relationships
    with other entities like artists, collections, and exhibitions.
    """

    # === IDENTIFICATION FIELDS ===
    # Using UUID for better security and avoiding sequential IDs
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="artworks")

    # === BASIC INFORMATION ===
    title = models.CharField(max_length=300, blank=True, verbose_name="Titre")
    # Many-to-many relationship allows artworks with multiple artists (collaborations)
    artists = models.ManyToManyField(Artist, blank=True, verbose_name="Artiste(s)")
    creation_year = models.IntegerField(
        null=True, blank=True, verbose_name="Année de création"
    )
    origin_country = models.CharField(
        max_length=100, blank=True, verbose_name="Pays d'origine"
    )

    # Foreign keys to reference models with SET_NULL to preserve data if a
    # reference is deleted
    art_type = models.ForeignKey(
        ArtType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Type d'art",
    )
    support = models.ForeignKey(
        Support,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Support",
    )
    technique = models.ForeignKey(
        Technique,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Technique",
    )

    # === PHYSICAL DIMENSIONS AND WEIGHT ===
    # Using DecimalField for precise measurements (max 999,999.99)
    height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Hauteur (cm)",
    )
    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Largeur (cm)",
    )
    depth = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Profondeur (cm)",
    )
    weight = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Poids (kg)"
    )

    # === ACQUISITION INFORMATION ===
    acquisition_date = models.DateField(
        null=True, blank=True, verbose_name="Date d'acquisition"
    )
    acquisition_place = models.CharField(
        max_length=200, blank=True, verbose_name="Lieu d'acquisition"
    )
    # Price field allows up to 99,999,999.99 (for expensive artworks)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix (€)"
    )
    provenance = models.TextField(blank=True, verbose_name="Provenance")

    # === STATUS AND LOCATION FIELDS ===
    # Boolean fields for quick status checks
    is_framed = models.BooleanField(default=False, verbose_name="Est encadrée")
    is_borrowed = models.BooleanField(default=False, verbose_name="Est empruntée")
    is_signed = models.BooleanField(default=False, verbose_name="Est signée")
    is_acquired = models.BooleanField(
        default=True, verbose_name="Est acquise"
    )  # False for wishlist items
    current_location = models.CharField(
        max_length=50,
        choices=LOCATIONS,
        default="domicile",
        verbose_name="Localisation actuelle",
    )

    # === RELATIONSHIPS ===
    # Many-to-many relationships for flexible associations
    collections = models.ManyToManyField(
        Collection, blank=True, verbose_name="Collection(s)"
    )
    exhibitions = models.ManyToManyField(
        Exhibition, blank=True, verbose_name="Exposition(s)"
    )
    # Self-referencing FK for artwork series or related pieces
    parent_artwork = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Œuvre parente",
    )
    # Text field for multiple owners (could be improved with a separate Owner model)
    owners = models.CharField(
        max_length=500, blank=True, verbose_name="Propriétaire(s)"
    )

    # === ADDITIONAL INFORMATION ===
    # Use a custom through model compatible with UUID primary keys
    tags = TaggableManager(
        verbose_name="Mots-clés", blank=True, through="UUIDTaggedItem"
    )
    contextual_references = models.TextField(
        blank=True, verbose_name="Références contextuelles"
    )
    notes = models.TextField(blank=True, verbose_name="Notes libres")

    # === METADATA ===
    created_at = models.DateTimeField(auto_now_add=True)  # Set once when created
    updated_at = models.DateTimeField(auto_now=True)  # Updated on every save
    last_exhibited = models.DateField(
        null=True, blank=True, verbose_name="Dernière exposition"
    )

    class Meta:
        ordering = ["-created_at"]  # Show newest artworks first
        verbose_name = "Œuvre d'art"
        verbose_name_plural = "Œuvres d'art"

    def __str__(self):
        """
        Return a meaningful string representation of the artwork.

        Priority order:
        1. Title if available
        2. "Artwork by [Artist(s)]" if artists exist
        3. "Artwork #[UUID prefix]" as fallback
        """
        if self.title:
            return self.title
        if self.artists.exists():
            artist_names = ", ".join(artist.name for artist in self.artists.all())
            return f"Œuvre de {artist_names}"
        return f"Œuvre #{str(self.id)[:8]}"

    def get_absolute_url(self):
        """Return the canonical URL for this artwork's detail view."""
        return reverse("artworks:detail", kwargs={"pk": self.pk})

    def get_artists_display(self):
        """
        Return a comma-separated string of all associated artists.

        Returns:
            str: Artist names joined by commas, or empty string if no artists.
        """
        return ", ".join([artist.name for artist in self.artists.all()])

    def get_dimensions_display(self):
        """
        Return a formatted string of artwork dimensions.

        Returns:
            str: Formatted dimensions string (e.g., "H: 50cm x L: 40cm")
                 or "Non spécifiées" if no dimensions are set.
        """
        dimensions = []
        if self.height:
            dimensions.append(f"H: {self.height}cm")
        if self.width:
            dimensions.append(f"L: {self.width}cm")
        if self.depth:
            dimensions.append(f"P: {self.depth}cm")
        return " x ".join(dimensions) if dimensions else "Non spécifiées"


class ArtworkPhoto(models.Model):
    """
    Model representing photos/images of artworks.

    Each artwork can have multiple photos, with one designated as primary.
    Images are automatically processed to create thumbnails for performance.
    """

    artwork = models.ForeignKey(
        Artwork, on_delete=models.CASCADE, related_name="photos"
    )
    # Images are organized by date in subdirectories for better file management
    # Image principale (redimensionnée au besoin lors de l'upload)
    image = ProcessedImageField(
        upload_to="artworks/",
        processors=[Transpose(), ResizeToFit(2000, 2000, upscale=False)],
        format="JPEG",  # garde le ratio ; change en fonction de ton besoin d'encodage
        options={"quality": 80, "optimize": True, "progressive": True},
        blank=True,
        null=True,
    )

    # Vignette générée à la volée pour les listes/cartes
    image_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFit(600, 600, upscale=False)],
        format="JPEG",
        options={"quality": 80},
    )

    # Affichage grande taille (pour les pages de détail)
    image_display = ImageSpecField(
        source="image",
        processors=[ResizeToFit(1200, 1200, upscale=False)],
        format="JPEG",
        options={"quality": 85},
    )

    caption = models.CharField(max_length=300, blank=True, verbose_name="Légende")
    is_primary = models.BooleanField(default=False, verbose_name="Photo principale")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Order by primary status first, then by creation date
        ordering = ["-is_primary", "created_at"]
        verbose_name = "Photo d'œuvre"
        verbose_name_plural = "Photos d'œuvres"

    def __str__(self):
        """Return a descriptive string for the photo."""
        return f"Photo de {self.artwork}"

    def save(self, *args, **kwargs):
        """
        Override save method to ensure only one primary photo per artwork.

        When a photo is marked as primary, all other photos of the same
        artwork are automatically unmarked as primary.
        """
        if self.is_primary:
            # Save first to get a primary key
            super().save(*args, **kwargs)
            # Then update other photos to remove primary status
            ArtworkPhoto.objects.filter(artwork=self.artwork).exclude(
                pk=self.pk
            ).update(is_primary=False)
        else:
            super().save(*args, **kwargs)


class ArtworkAttachment(models.Model):
    """
    Generic file attachment linked to an artwork.

    Supports common document formats (PDF, ODT, Office) and images. Used to
    store invoices, certificates, condition reports, etc.
    """

    artwork = models.ForeignKey(
        Artwork, on_delete=models.CASCADE, related_name="attachments"
    )
    title = models.CharField(max_length=255, blank=True, verbose_name="Titre")
    file = models.FileField(
        upload_to="artwork_attachments/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "odt",
                    "doc",
                    "docx",
                    "xls",
                    "xlsx",
                    "csv",
                    "jpg",
                    "jpeg",
                    "png",
                    "tif",
                    "tiff",
                    "zip",
                ]
            )
        ],
        verbose_name="Fichier",
    )
    notes = models.CharField(max_length=500, blank=True, verbose_name="Notes")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"

    def __str__(self) -> str:
        label = self.title or (self.file.name.split("/")[-1] if self.file else "")
        return f"Pièce jointe de {self.artwork}: {label}".strip()


class WishlistItem(models.Model):
    """
    Model representing items on a user's wishlist.

    Wishlist items are artworks that users want to acquire but don't own yet.
    They contain basic information and priority levels for planning purchases.
    """

    # Priority choices for organizing wishlist items
    PRIORITY_CHOICES = [
        (1, "Haute"),  # High priority
        (2, "Moyenne"),  # Medium priority
        (3, "Basse"),  # Low priority
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    title = models.CharField(max_length=300, verbose_name="Titre", default="Général")
    # Artist name as text field since the artist might not be in the database yet
    artist_name = models.CharField(max_length=200, blank=True, verbose_name="Artiste")
    estimated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Prix estimé (€)",
    )
    priority = models.IntegerField(
        default=3, choices=PRIORITY_CHOICES, verbose_name="Priorité"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    # URL to source where the artwork was found (gallery, auction site, etc.)
    source_url = models.URLField(blank=True, verbose_name="URL source")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Order by priority (high first), then by creation date (newest first)
        ordering = ["priority", "-created_at"]
        verbose_name = "Œuvre convoitée"
        verbose_name_plural = "Œuvres convoitées"

    def __str__(self):
        """Return the wishlist item's title as string representation."""
        return self.title


class UUIDTaggedItem(GenericUUIDTaggedItemBase):
    tag = models.ForeignKey(
        Tag,
        related_name="artworks_%(app_label)s_%(class)s_items",
        on_delete=models.CASCADE,
    )
