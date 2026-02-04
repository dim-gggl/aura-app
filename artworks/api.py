"""
API views for the artworks app.

This module defines the API endpoints for the artworks app,
including Artwork and Artist models. It uses Django REST Framework
to provide CRUD operations and pagination for the API.
"""

from django.db.models import Prefetch
from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Artist, Artwork
from .serializers import ArtistSerializer, ArtworkSerializer


class DefaultPagination(PageNumberPagination):
    """
    Default pagination settings for API responses.

    This class defines the default pagination settings for the API,
    including the page size, page size query parameter, and maximum
    page size.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class UserScopedMixin:
    """
    Mixin for API views that require user-specific data.

    This mixin ensures that the queryset only returns objects
    that belong to the authenticated user.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class ArtworkViewSet(UserScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for Artwork model.

    This ViewSet provides CRUD operations for the Artwork model,
    including listing, retrieving, creating, updating, and deleting
    artworks. It uses the ArtworkSerializer to serialize the data.
    """

    queryset = Artwork._default_manager.all().prefetch_related(
        "artists",
        Prefetch("photos"),
        "collections",
    )
    serializer_class = ArtworkSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ArtistViewSet(UserScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for Artist model.

    This ViewSet provides CRUD operations for the Artist model,
    including listing, retrieving, creating, updating, and deleting
    artists. It uses the ArtistSerializer to serialize the data.
    """

    queryset = Artist._default_manager.all()
    serializer_class = ArtistSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        return super().get_queryset().order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
