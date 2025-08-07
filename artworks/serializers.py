from rest_framework import serializers
from .models import Artwork, Artist

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ["id", "name", "birth_year", "death_year"]

class ArtworkSerializer(serializers.ModelSerializer):
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
        artists = validated_data.pop("artists", [])
        artwork = super().create(validated_data)
        if artists:
            artwork.artists.set(artists)
        return artwork

    def update(self, instance, validated_data):
        artists = validated_data.pop("artists", None)
        instance = super().update(instance, validated_data)
        if artists is not None:
            instance.artists.set(artists)
        return instance