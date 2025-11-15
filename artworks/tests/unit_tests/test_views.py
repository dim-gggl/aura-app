from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from artworks.models import (
    Artist,
    ArtType,
    Artwork,
    Collection,
    Exhibition,
    Keyword,
    Support,
    Technique,
    WishlistItem,
)

User = get_user_model()


@pytest.fixture
def client():
    """Fixture pour le client de test Django."""
    return Client()


@pytest.fixture
def user():
    """Fixture pour créer un utilisateur de test."""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpassword123"
    )


@pytest.fixture
def other_user():
    """Fixture pour créer un autre utilisateur (pour tester la sécurité)."""
    return User.objects.create_user(
        username="otheruser", email="other@example.com", password="otherpassword123"
    )


@pytest.fixture
def artist():
    """Fixture pour créer un artiste de test."""
    return Artist.objects.create(
        name="Vincent van Gogh",
        birth_year=1853,
        death_year=1890,
        nationality="Néerlandais",
        biography="Peintre post-impressionniste néerlandais",
    )


@pytest.fixture
def collection(user):
    """Fixture pour créer une collection de test."""
    return Collection.objects.create(
        user=user,
        name="Ma Collection Test",
        description="Une collection pour les tests",
    )


@pytest.fixture
def exhibition(user):
    """Fixture pour créer une exposition de test."""
    return Exhibition.objects.create(
        user=user,
        name="Exposition Test",
        location="Musée Test",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        description="Une exposition pour les tests",
    )


@pytest.fixture
def art_type():
    """Fixture pour créer un type d'art de test."""
    return ArtType.objects.create(name="Peinture")


@pytest.fixture
def support():
    """Fixture pour créer un support de test."""
    return Support.objects.create(name="Toile")


@pytest.fixture
def technique():
    """Fixture pour créer une technique de test."""
    return Technique.objects.create(name="Huile sur toile")


@pytest.fixture
def keyword():
    """Fixture pour créer un mot-clé de test."""
    return Keyword.objects.create(name="Impressionnisme")


@pytest.fixture
def artwork(
    user, artist, art_type, support, technique, collection, exhibition, keyword
):
    """Fixture pour créer une œuvre d'art complète de test."""
    artwork = Artwork.objects.create(
        user=user,
        title="La Nuit étoilée",
        creation_year=1889,
        origin_country="France",
        art_type=art_type,
        support=support,
        technique=technique,
        height=Decimal("73.7"),
        width=Decimal("92.1"),
        is_signed=True,
        is_acquired=True,
        current_location="domicile",
    )
    artwork.artists.add(artist)
    artwork.collections.add(collection)
    artwork.exhibitions.add(exhibition)
    artwork.keywords.add(keyword)
    return artwork


@pytest.fixture
def wishlist_item(user):
    """Fixture pour créer un élément de wishlist de test."""
    return WishlistItem.objects.create(
        user=user,
        title="Œuvre Convoitée",
        artist_name="Artiste Célèbre",
        estimated_price=Decimal("50000.00"),
        priority=1,
        notes="Très belle œuvre",
    )


@pytest.fixture
def authenticated_client(client, user):
    """Fixture pour un client authentifié."""
    client.force_login(user)
    return client


# Tests pour les vues CRUD d'Artwork
@pytest.mark.django_db
class TestArtworkViews:

    def test_artwork_list_view_authenticated(self, authenticated_client, artwork):
        """Test l'affichage de la liste des œuvres pour un utilisateur authentifié."""
        url = reverse("artworks:list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "filter" in response.context
        assert "page_obj" in response.context
        assert artwork in response.context["page_obj"].object_list
        assert "La Nuit étoilée" in response.content.decode()

    def test_artwork_list_view_unauthenticated(self, client):
        """Test que la liste des œuvres redirige vers login si non authentifié."""
        url = reverse("artworks:list")
        response = client.get(url)

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_artwork_list_view_filters_by_user(
        self, authenticated_client, user, other_user, artwork
    ):
        """Test que la liste ne montre que les œuvres de l'utilisateur connecté."""
        # Créer une œuvre pour un autre utilisateur
        other_artwork = Artwork.objects.create(
            user=other_user, title="Œuvre d'un autre utilisateur"
        )

        url = reverse("artworks:list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        artworks_in_context = list(response.context["page_obj"].object_list)
        assert artwork in artworks_in_context
        assert other_artwork not in artworks_in_context

    def test_artwork_detail_view_authenticated(self, authenticated_client, artwork):
        """Test l'affichage du détail d'une œuvre."""
        url = reverse("artworks:detail", kwargs={"pk": artwork.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["artwork"] == artwork
        assert "photos" in response.context
        assert "La Nuit étoilée" in response.content.decode()

    def test_artwork_detail_view_wrong_user(self, authenticated_client, other_user):
        """Test qu'on ne peut pas voir l'œuvre d'un autre utilisateur."""
        other_artwork = Artwork.objects.create(
            user=other_user, title="Œuvre d'un autre utilisateur"
        )

        url = reverse("artworks:detail", kwargs={"pk": other_artwork.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 404

    def test_artwork_detail_view_unauthenticated(self, client, artwork):
        """Test que le détail redirige vers login si non authentifié."""
        url = reverse("artworks:detail", kwargs={"pk": artwork.pk})
        response = client.get(url)

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_artwork_create_view_get_authenticated(self, authenticated_client):
        """Test l'affichage du formulaire de création d'œuvre."""
        url = reverse("artworks:create")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert "photo_formset" in response.context
        assert response.context["title"] == "Ajouter une œuvre"

    def test_artwork_create_view_post_valid(
        self, authenticated_client, user, artist, art_type
    ):
        """Test la création d'une œuvre avec des données valides."""
        url = reverse("artworks:create")
        data = {
            "title": "Nouvelle Œuvre Test",
            "artists": [artist.pk],
            "creation_year": 2023,
            "art_type": art_type.pk,
            "is_acquired": True,
            "current_location": "domicile",
            # Données pour le formset de photos (vide)
            "photos-TOTAL_FORMS": "0",
            "photos-INITIAL_FORMS": "0",
            "photos-MIN_NUM_FORMS": "0",
            "photos-MAX_NUM_FORMS": "1000",
        }

        response = authenticated_client.post(url, data)

        # Vérifier la redirection
        assert response.status_code == 302

        # Vérifier que l'œuvre a été créée
        artwork = Artwork.objects.get(title="Nouvelle Œuvre Test")
        assert artwork.user == user
        assert artist in artwork.artists.all()
        assert artwork.art_type == art_type

        # Vérifier la redirection vers le détail
        assert response.url == reverse("artworks:detail", kwargs={"pk": artwork.pk})

    def test_artwork_create_view_post_invalid(self, authenticated_client):
        """Test la création d'œuvre avec des données invalides."""
        url = reverse("artworks:create")
        data = {
            # Pas de titre - données invalides
            "creation_year": "invalid_year",  # Année invalide
            "photos-TOTAL_FORMS": "0",
            "photos-INITIAL_FORMS": "0",
            "photos-MIN_NUM_FORMS": "0",
            "photos-MAX_NUM_FORMS": "1000",
        }

        response = authenticated_client.post(url, data)

        # Doit rester sur la page du formulaire
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_artwork_update_view_get(self, authenticated_client, artwork):
        """Test l'affichage du formulaire de modification d'œuvre."""
        url = reverse("artworks:update", kwargs={"pk": artwork.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert "photo_formset" in response.context
        assert response.context["artwork"] == artwork
        assert response.context["title"] == 'Modifier l"œuvre'

    def test_artwork_update_view_post_valid(self, authenticated_client, artwork):
        """Test la modification d'une œuvre avec des données valides."""
        url = reverse("artworks:update", kwargs={"pk": artwork.pk})
        data = {
            "title": "Titre Modifié",
            "creation_year": 1890,  # Changement d'année
            "current_location": "exposee",  # Changement de localisation
            "is_acquired": True,
            # Données pour le formset de photos
            "photos-TOTAL_FORMS": "0",
            "photos-INITIAL_FORMS": "0",
            "photos-MIN_NUM_FORMS": "0",
            "photos-MAX_NUM_FORMS": "1000",
        }

        response = authenticated_client.post(url, data)

        # Vérifier la redirection
        assert response.status_code == 302
        assert response.url == reverse("artworks:detail", kwargs={"pk": artwork.pk})

        # Vérifier que l'œuvre a été modifiée
        artwork.refresh_from_db()
        assert artwork.title == "Titre Modifié"
        assert artwork.creation_year == 1890
        assert artwork.current_location == "exposee"

    def test_artwork_update_view_wrong_user(self, authenticated_client, other_user):
        """Test qu'on ne peut pas modifier l'œuvre d'un autre utilisateur."""
        other_artwork = Artwork.objects.create(
            user=other_user, title="Œuvre d'un autre utilisateur"
        )

        url = reverse("artworks:update", kwargs={"pk": other_artwork.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 404

    def test_artwork_delete_view_get(self, authenticated_client, artwork):
        """Test l'affichage de la page de confirmation de suppression."""
        url = reverse("artworks:delete", kwargs={"pk": artwork.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["artwork"] == artwork
        assert "La Nuit étoilée" in response.content.decode()

    def test_artwork_delete_view_post(self, authenticated_client, artwork):
        """Test la suppression d'une œuvre."""
        artwork_pk = artwork.pk
        url = reverse("artworks:delete", kwargs={"pk": artwork_pk})

        response = authenticated_client.post(url)

        # Vérifier la redirection
        assert response.status_code == 302
        assert response.url == reverse("artworks:list")

        # Vérifier que l'œuvre a été supprimée
        assert not Artwork.objects.filter(pk=artwork_pk).exists()

    def test_artwork_delete_view_wrong_user(self, authenticated_client, other_user):
        """Test qu'on ne peut pas supprimer l'œuvre d'un autre utilisateur."""
        other_artwork = Artwork.objects.create(
            user=other_user, title="Œuvre d'un autre utilisateur"
        )

        url = reverse("artworks:delete", kwargs={"pk": other_artwork.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 404

        # Vérifier que l'œuvre n'a pas été supprimée
        assert Artwork.objects.filter(pk=other_artwork.pk).exists()


# Tests pour les vues d'export et suggestion aléatoire
@pytest.mark.django_db
class TestArtworkSpecialViews:

    def test_artwork_export_html_view(self, authenticated_client, artwork):
        """Test l'export HTML d'une œuvre."""
        url = reverse("artworks:export_html", kwargs={"pk": artwork.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "text/html"
        assert (
            f"attachment; filename='artwork_{artwork.pk}.html'"
            in response["Content-Disposition"]
        )
        assert "La Nuit étoilée" in response.content.decode()

    def test_artwork_export_html_wrong_user(self, authenticated_client, other_user):
        """Test qu'on ne peut pas exporter l'œuvre d'un autre utilisateur."""
        other_artwork = Artwork.objects.create(
            user=other_user, title="Œuvre d'un autre utilisateur"
        )

        url = reverse("artworks:export_html", kwargs={"pk": other_artwork.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 404

    @patch("weasyprint.HTML")
    def test_artwork_export_pdf_view_success(
        self, mock_html, authenticated_client, artwork
    ):
        """Test l'export PDF d'une œuvre (avec WeasyPrint disponible)."""
        # Mock de WeasyPrint
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.write_pdf.return_value = b"fake_pdf_content"
        mock_html.return_value = mock_pdf_instance

        url = reverse("artworks:export_pdf", kwargs={"pk": artwork.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert (
            f"attachment; filename='artwork_{artwork.pk}.pdf'"
            in response["Content-Disposition"]
        )
        assert response.content == b"fake_pdf_content"

    @patch("weasyprint.HTML", side_effect=ImportError("WeasyPrint not available"))
    def test_artwork_export_pdf_view_no_weasyprint(
        self, mock_html, authenticated_client, artwork
    ):
        """Test l'export PDF quand WeasyPrint n'est pas disponible."""
        url = reverse("artworks:export_pdf", kwargs={"pk": artwork.pk})
        response = authenticated_client.get(url)

        # Doit rediriger vers le détail avec un message d'erreur
        assert response.status_code == 302
        assert response.url == reverse("artworks:detail", kwargs={"pk": artwork.pk})

    def test_random_suggestion_with_artworks(self, authenticated_client, user):
        """Test la suggestion aléatoire quand il y a des œuvres disponibles."""
        # Créer une œuvre non exposée depuis longtemps
        old_date = datetime.now().date() - timedelta(days=200)
        artwork = Artwork.objects.create(
            user=user,
            title="Œuvre à suggérer",
            current_location="domicile",
            last_exhibited=old_date,
        )

        url = reverse("artworks:random_suggestion")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["artwork"] == artwork
        assert "no_suggestion" not in response.context
        assert "Œuvre à suggérer" in response.content.decode()

    def test_random_suggestion_no_artworks(self, authenticated_client, user):
        """Test la suggestion aléatoire quand il n'y a pas d'œuvres disponibles."""
        # Créer une œuvre récemment exposée (ne sera pas suggérée)
        recent_date = datetime.now().date() - timedelta(days=30)
        Artwork.objects.create(
            user=user,
            title="Œuvre récemment exposée",
            current_location="exposee",
            last_exhibited=recent_date,
        )

        url = reverse("artworks:random_suggestion")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["no_suggestion"] is True
        assert "artwork" not in response.context
        assert "Toutes vos œuvres sont à jour" in response.content.decode()

    def test_random_suggestion_filters_by_location_and_date(
        self, authenticated_client, user
    ):
        """Test que la suggestion filtre correctement par localisation et date."""
        old_date = datetime.now().date() - timedelta(days=200)
        recent_date = datetime.now().date() - timedelta(days=30)

        # Œuvre éligible (domicile, ancienne exposition)
        eligible_artwork = Artwork.objects.create(
            user=user,
            title="Œuvre éligible",
            current_location="domicile",
            last_exhibited=old_date,
        )

        # Œuvres non éligibles
        Artwork.objects.create(
            user=user,
            title="Œuvre en exposition",
            current_location="exposee",
            last_exhibited=old_date,
        )

        Artwork.objects.create(
            user=user,
            title="Œuvre récemment exposée",
            current_location="domicile",
            last_exhibited=recent_date,
        )

        url = reverse("artworks:random_suggestion")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["artwork"] == eligible_artwork
        assert "Œuvre éligible" in response.content.decode()


# Tests pour les vues Wishlist
@pytest.mark.django_db
class TestWishlistViews:

    def test_wishlist_view_get(self, authenticated_client, wishlist_item):
        """Test l'affichage de la wishlist."""
        url = reverse("artworks:wishlist")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "items" in response.context
        assert "form" in response.context
        assert wishlist_item in response.context["items"]
        assert "Œuvre Convoitée" in response.content.decode()

    def test_wishlist_view_post_valid(self, authenticated_client, user):
        """Test l'ajout d'un élément à la wishlist."""
        url = reverse("artworks:wishlist")
        data = {
            "title": "Nouvelle Œuvre Convoitée",
            "artist_name": "Picasso",
            "estimated_price": "100000.00",
            "priority": 2,
            "notes": "Une très belle œuvre",
        }

        response = authenticated_client.post(url, data)

        # Vérifier la redirection
        assert response.status_code == 302
        assert response.url == reverse("artworks:wishlist")

        # Vérifier que l'élément a été créé
        item = WishlistItem.objects.get(title="Nouvelle Œuvre Convoitée")
        assert item.user == user
        assert item.artist_name == "Picasso"
        assert item.priority == 2

    def test_wishlist_view_post_invalid(self, authenticated_client):
        """Test l'ajout d'un élément invalide à la wishlist."""
        url = reverse("artworks:wishlist")
        data = {
            # Pas de titre - données invalides
            "artist_name": "Picasso",
            "estimated_price": "invalid_price",  # Prix invalide
        }

        response = authenticated_client.post(url, data)

        # Doit rester sur la page avec le formulaire
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_wishlist_filters_by_user(
        self, authenticated_client, user, other_user, wishlist_item
    ):
        """Test que la wishlist ne montre que les éléments de l'utilisateur connecté."""
        # Créer un élément pour un autre utilisateur
        other_item = WishlistItem.objects.create(
            user=other_user, title="Élément d'un autre utilisateur"
        )

        url = reverse("artworks:wishlist")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        items_in_context = list(response.context["items"])
        assert wishlist_item in items_in_context
        assert other_item not in items_in_context

    def test_wishlist_delete_view_get(self, authenticated_client, wishlist_item):
        """Test l'affichage de la page de confirmation de suppression."""
        url = reverse("artworks:wishlist_delete", kwargs={"pk": wishlist_item.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["item"] == wishlist_item
        assert "Œuvre Convoitée" in response.content.decode()

    def test_wishlist_delete_view_post(self, authenticated_client, wishlist_item):
        """Test la suppression d'un élément de wishlist."""
        item_pk = wishlist_item.pk
        url = reverse("artworks:wishlist_delete", kwargs={"pk": item_pk})

        response = authenticated_client.post(url)

        # Vérifier la redirection
        assert response.status_code == 302
        assert response.url == reverse("artworks:wishlist")

        # Vérifier que l'élément a été supprimé
        assert not WishlistItem.objects.filter(pk=item_pk).exists()

    def test_wishlist_delete_view_wrong_user(self, authenticated_client, other_user):
        """Test qu'on ne peut pas supprimer l'élément d'un autre utilisateur."""
        other_item = WishlistItem.objects.create(
            user=other_user, title="Élément d'un autre utilisateur"
        )

        url = reverse("artworks:wishlist_delete", kwargs={"pk": other_item.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 404

        # Vérifier que l'élément n'a pas été supprimé
        assert WishlistItem.objects.filter(pk=other_item.pk).exists()


# Tests pour les vues CRUD d'Artist
@pytest.mark.django_db
class TestArtistViews:

    def test_artist_list_view_authenticated(self, authenticated_client, user, artist):
        """Test l'affichage de la liste des artistes."""
        # Créer une œuvre pour associer l'artiste à l'utilisateur
        Artwork.objects.create(user=user, title="Test").artists.add(artist)

        url = reverse("artworks:artist_list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "page_obj" in response.context
        assert artist in response.context["page_obj"].object_list
        assert "Vincent van Gogh" in response.content.decode()

    def test_artist_list_view_with_search(self, authenticated_client, user):
        """Test la recherche dans la liste des artistes."""
        # Créer des artistes
        artist1 = Artist.objects.create(name="Pablo Picasso")
        artist2 = Artist.objects.create(name="Claude Monet")

        # Associer les artistes à des œuvres de l'utilisateur
        Artwork.objects.create(user=user, title="Test1").artists.add(artist1)
        Artwork.objects.create(user=user, title="Test2").artists.add(artist2)

        # Recherche de "Picasso"
        url = reverse("artworks:artist_list")
        response = authenticated_client.get(url, {"search": "Picasso"})

        assert response.status_code == 200
        artists_in_context = list(response.context["page_obj"].object_list)
        assert artist1 in artists_in_context
        assert artist2 not in artists_in_context
        assert "Pablo Picasso" in response.content.decode()
        assert "Claude Monet" not in response.content.decode()

    def test_artist_detail_view(self, authenticated_client, user, artist):
        """Test l'affichage du détail d'un artiste."""
        # Créer une œuvre pour l'artiste
        artwork = Artwork.objects.create(user=user, title="Œuvre test")
        artwork.artists.add(artist)

        url = reverse("artworks:artist_detail", kwargs={"pk": artist.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["artist"] == artist
        assert "artworks" in response.context
        assert artwork in response.context["artworks"]
        assert "Vincent van Gogh" in response.content.decode()

    def test_artist_create_view_get(self, authenticated_client):
        """Test l'affichage du formulaire de création d'artiste."""
        url = reverse("artworks:artist_create")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["title"] == "Ajouter un artiste"

    def test_artist_create_view_post_valid(self, authenticated_client):
        """Test la création d'un artiste avec des données valides."""
        url = reverse("artworks:artist_create")
        data = {
            "name": "Frida Kahlo",
            "birth_year": 1907,
            "death_year": 1954,
            "nationality": "Mexicaine",
            "biography": "Peintre mexicaine surréaliste",
        }

        response = authenticated_client.post(url, data)

        # Vérifier la redirection
        assert response.status_code == 302

        # Vérifier que l'artiste a été créé
        artist = Artist.objects.get(name="Frida Kahlo")
        assert artist.birth_year == 1907
        assert artist.nationality == "Mexicaine"

        # Vérifier la redirection vers le détail
        assert response.url == reverse(
            "artworks:artist_detail", kwargs={"pk": artist.pk}
        )

    def test_artist_create_view_post_invalid(self, authenticated_client):
        """Test la création d'artiste avec des données invalides."""
        url = reverse("artworks:artist_create")
        data = {
            # Pas de nom - données invalides
            "birth_year": "invalid_year",
        }

        response = authenticated_client.post(url, data)

        # Doit rester sur la page du formulaire
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_artist_update_view_get(self, authenticated_client, artist):
        """Test l'affichage du formulaire de modification d'artiste."""
        url = reverse("artworks:artist_update", kwargs={"pk": artist.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["artist"] == artist
        assert response.context["title"] == 'Modifier l"artiste'

    def test_artist_update_view_post_valid(self, authenticated_client, artist):
        """Test la modification d'un artiste avec des données valides."""
        url = reverse("artworks:artist_update", kwargs={"pk": artist.pk})
        data = {
            "name": "Vincent van Gogh (modifié)",
            "birth_year": 1853,
            "death_year": 1890,
            "nationality": "Néerlandais",
            "biography": "Peintre post-impressionniste néerlandais - modifié",
        }

        response = authenticated_client.post(url, data)

        # Vérifier la redirection
        assert response.status_code == 302
        assert response.url == reverse(
            "artworks:artist_detail", kwargs={"pk": artist.pk}
        )

        # Vérifier que l'artiste a été modifié
        artist.refresh_from_db()
        assert artist.name == "Vincent van Gogh (modifié)"
        assert artist.biography == "Peintre post-impressionniste néerlandais - modifié"


# Tests pour les vues CRUD de Collection
@pytest.mark.django_db
class TestCollectionViews:

    def test_collection_list_view_authenticated(self, authenticated_client, collection):
        """Test l'affichage de la liste des collections."""
        url = reverse("artworks:collection_list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "page_obj" in response.context
        assert collection in response.context["page_obj"].object_list
        assert "Ma Collection Test" in response.content.decode()

    def test_collection_list_view_with_search(self, authenticated_client, user):
        """Test la recherche dans la liste des collections."""
        collection1 = Collection.objects.create(user=user, name="Collection Moderne")
        collection2 = Collection.objects.create(
            user=user, name="Collection Classique", description="Art classique"
        )

        # Recherche par nom
        url = reverse("artworks:collection_list")
        response = authenticated_client.get(url, {"search": "Moderne"})

        assert response.status_code == 200
        collections_in_context = list(response.context["page_obj"].object_list)
        assert collection1 in collections_in_context
        assert collection2 not in collections_in_context

        # Recherche par description
        response = authenticated_client.get(url, {"search": "classique"})
        collections_in_context = list(response.context["page_obj"].object_list)
        assert collection2 in collections_in_context

    def test_collection_list_filters_by_user(
        self, authenticated_client, user, other_user, collection
    ):
        """Test que la liste ne montre que les collections de l'utilisateur connecté."""
        other_collection = Collection.objects.create(
            user=other_user, name="Collection autre utilisateur"
        )

        url = reverse("artworks:collection_list")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        collections_in_context = list(response.context["page_obj"].object_list)
        assert collection in collections_in_context
        assert other_collection not in collections_in_context

    def test_collection_detail_view(self, authenticated_client, user, collection):
        """Test l'affichage du détail d'une collection."""
        # Créer une œuvre dans la collection
        artwork = Artwork.objects.create(user=user, title="Œuvre test")
        artwork.collections.add(collection)

        url = reverse("artworks:collection_detail", kwargs={"pk": collection.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["collection"] == collection
        assert "artworks" in response.context
        assert artwork in response.context["artworks"]
        assert "Ma Collection Test" in response.content.decode()

    def test_collection_detail_view_wrong_user(self, authenticated_client, other_user):
        """Test qu'on ne peut pas voir la collection d'un autre utilisateur."""
        other_collection = Collection.objects.create(
            user=other_user, name="Collection autre utilisateur"
        )

        url = reverse("artworks:collection_detail", kwargs={"pk": other_collection.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 404

    def test_collection_create_view_get(self, authenticated_client):
        """Test l'affichage du formulaire de création de collection."""
        url = reverse("artworks:collection_create")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["title"] == "Créer une collection"

    def test_collection_create_view_post_valid(self, authenticated_client, user):
        """Test la création d'une collection avec des données valides."""
        url = reverse("artworks:collection_create")
        data = {
            "name": "Nouvelle Collection",
            "description": "Description de la nouvelle collection",
        }

        response = authenticated_client.post(url, data)

        # Vérifier la redirection
        assert response.status_code == 302

        # Vérifier que la collection a été créée
        collection = Collection.objects.get(name="Nouvelle Collection")
        assert collection.user == user
        assert collection.description == "Description de la nouvelle collection"

        # Vérifier la redirection vers le détail
        assert response.url == reverse(
            "artworks:collection_detail", kwargs={"pk": collection.pk}
        )

    def test_collection_update_view_get(self, authenticated_client, collection):
        """Test l'affichage du formulaire de modification de collection."""
        url = reverse("artworks:collection_update", kwargs={"pk": collection.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["collection"] == collection
        assert response.context["title"] == "Modifier la collection"

    def test_collection_update_view_post_valid(self, authenticated_client, collection):
        """Test la modification d'une collection avec des données valides."""
        url = reverse("artworks:collection_update", kwargs={"pk": collection.pk})
        data = {"name": "Collection Modifiée", "description": "Description modifiée"}

        response = authenticated_client.post(url, data)

        # Vérifier la redirection
        assert response.status_code == 302
        assert response.url == reverse(
            "artworks:collection_detail", kwargs={"pk": collection.pk}
        )

        # Vérifier que la collection a été modifiée
        collection.refresh_from_db()
        assert collection.name == "Collection Modifiée"
        assert collection.description == "Description modifiée"

    def test_collection_update_view_wrong_user(self, authenticated_client, other_user):
        """Test qu'on ne peut pas modifier la collection d'un autre utilisateur."""
        other_collection = Collection.objects.create(
            user=other_user, name="Collection autre utilisateur"
        )

        url = reverse("artworks:collection_update", kwargs={"pk": other_collection.pk})
        response = authenticated_client.get(url)

        assert response.status_code == 404
