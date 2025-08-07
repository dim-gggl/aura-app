from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from django.db.models import Prefetch

from .models import Artwork, Artist
from .serializers import ArtworkSerializer, ArtistSerializer


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class UserScopedMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class ArtworkViewSet(UserScopedMixin, viewsets.ModelViewSet):
    serializer_class = ArtworkSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        qs = Artwork.objects.all().select_related("primary_artist").prefetch_related(
            "artists",
            Prefetch("photos"),
            "collections",
        )
        return super().get_queryset().filter(pk__in=qs.values("pk"))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ArtistViewSet(UserScopedMixin, viewsets.ModelViewSet):
    serializer_class = ArtistSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        return super().get_queryset().order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)