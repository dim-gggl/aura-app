"""
Serializers for the artworks app.

This module defines serializers for the Artwork and Artist models,
used for API endpoints and data serialization.
"""

from django.db.models import Q
from rest_framework import serializers

from .models import Artist, Artwork


class ArtistSerializer(serializers.ModelSerializer):
    """
    Serializer for the Artist model.

    This serializer converts Artist model instances into JSON format
    for API responses. It includes fields for the artist's ID, name,
    birth year, and death year.
    """

    class Meta:
        model = Artist
        fields = ["id", "name", "birth_year", "death_year"]


class ArtworkSerializer(serializers.ModelSerializer):
    """
    Serializer for the Artwork model.

    This serializer converts Artwork model instances into JSON format
    for API responses. It includes fields for the artwork's ID, title,
    year created, country, status, artists, and artist IDs.
    """

    artists = ArtistSerializer(many=True, read_only=True)
    # Champs exposés par l'API, mappés vers les champs du modèle
    year_created = serializers.IntegerField(
        source="creation_year", required=False, allow_null=True
    )
    country = serializers.CharField(
        source="origin_country", required=False, allow_blank=True
    )
    status = serializers.CharField(
        source="current_location", required=False, allow_blank=True
    )
    artist_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Artist._default_manager.none(),
        source="artists",
    )

    class Meta:
        model = Artwork
        fields = [
            "id",
            "title",
            "year_created",
            "country",
            "status",
            "artists",
            "artist_ids",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request") if hasattr(self, "context") else None
        if (
            request
            and hasattr(request, "user")
            and request.user
            and request.user.is_authenticated
        ):
            # Limit selectable artists to the current user's artists or shared
            # records where the user reference is null
            self.fields["artist_ids"].queryset = Artist._default_manager.filter(
                Q(user=request.user) | Q(user__isnull=True)
            )
        else:
            # No request in context → disallow arbitrary cross-tenant linking
            self.fields["artist_ids"].queryset = Artist._default_manager.none()

    def create(self, validated_data):
        """
        Create a new Artwork instance with associated artists.

        This method overrides the default create method to handle
        the creation of an Artwork with associated Artist instances.
        It ensures that the artists are properly linked to the artwork.
        """
        artists = validated_data.pop("artists", [])
        artwork = super().create(validated_data)
        if artists:
            artwork.artists.set(artists)
        return artwork

    def update(self, instance, validated_data):
        """
        Update an existing Artwork instance with associated artists.

        This method overrides the default update method to handle
        the update of an Artwork with associated Artist instances.
        It ensures that the artists are properly linked to the artwork.
        """
        artists = validated_data.pop("artists", None)
        instance = super().update(instance, validated_data)
        if artists is not None:
            instance.artists.set(artists)
        return instance
