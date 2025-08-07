from django.urls import path, include
from rest_framework.routers import DefaultRouter
from artworks.api import ArtworkViewSet, ArtistViewSet
from contacts.api import ContactViewSet
from notes.api import NoteViewSet

router = DefaultRouter()
router.register(r"artworks", ArtworkViewSet, basename="artwork")
router.register(r"artists", ArtistViewSet, basename="artist")
router.register(r"contacts", ContactViewSet, basename="contact")
router.register(r"notes", NoteViewSet, basename="note")

urlpatterns = [
    path("", include(router.urls)),
]