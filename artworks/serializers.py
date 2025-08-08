"""
Serializers for the artworks app.

This module defines serializers for the Artwork and Artist models,
used for API endpoints and data serialization.
"""

from rest_framework import serializers
from .models import Artwork, Artist


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
    artist_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Artist.objects.all(), source="artists"
    )

    class Meta:
        model = Artwork
        fields = [
            "id", "title", "year_created", "country", "status",
            "artists", "artist_ids",
        ]

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