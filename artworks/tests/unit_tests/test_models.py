from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError

from artworks.models import (Artist, ArtType, Artwork, ArtworkPhoto,
                             Collection, Exhibition, Keyword, Support,
                             Technique, WishlistItem)
from core.models import User


@pytest.fixture
def user():
    """Fixture pour créer un utilisateur de test."""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpassword"
    )


@pytest.fixture
def artist():
    """Fixture pour créer un artiste de test."""
    return Artist.objects.create(
        name="Leonardo da Vinci",
        birth_year=1452,
        death_year=1519,
        nationality="Italien",
        biography=(
            "Leonardo da Vinci était un artiste, scientifique et polymathe italien."
        ),
    )


@pytest.fixture
def collection(user):
    """Fixture pour créer une collection de test."""
    return Collection.objects.create(
        user=user, name="Ma Collection", description="Une belle collection d'art"
    )


@pytest.fixture
def exhibition(user):
    """Fixture pour créer une exposition de test."""
    return Exhibition.objects.create(
        user=user,
        name="Exposition Renaissance",
        location="Musée du Louvre",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        description="Une exposition sur la Renaissance",
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
    return Keyword.objects.create(name="Renaissance")


@pytest.fixture
def artwork(user, artist, art_type, support, technique):
    """Fixture pour créer une œuvre d'art de test."""
    artwork = Artwork.objects.create(
        user=user,
        title="Mona Lisa",
        creation_year=1503,
        origin_country="Italie",
        art_type=art_type,
        support=support,
        technique=technique,
        height=Decimal("77.00"),
        width=Decimal("53.00"),
        depth=Decimal("0.00"),
        weight=Decimal("0.00"),
        acquisition_date=date(1503, 1, 1),
        acquisition_place="Louvre",
        price=Decimal("0.00"),
        provenance="Louvre",
        is_framed=False,
        is_borrowed=False,
        is_signed=True,
        is_acquired=True,
        current_location="domicile",
        owners="Louvre",
        contextual_references="Chef-d'œuvre de la Renaissance",
        notes="Œuvre emblématique",
        last_exhibited=date(1503, 1, 1),
    )
    artwork.artists.add(artist)
    return artwork


# Tests pour le modèle Artist
@pytest.mark.django_db
class TestArtistModel:

    def test_artist_creation(self, artist):
        """Test la création d'un artiste."""
        assert artist.name == "Leonardo da Vinci"
        assert artist.birth_year == 1452
        assert artist.death_year == 1519
        assert artist.nationality == "Italien"
        assert artist.biography is not None
        assert artist.created_at is not None
        assert artist.updated_at is not None

    def test_artist_str_method(self, artist):
        """Test la méthode __str__ de Artist."""
        assert str(artist) == "Leonardo da Vinci"

    def test_artist_ordering(self):
        """Test l'ordre par défaut des artistes."""
        Artist.objects.create(name="Picasso")
        Artist.objects.create(name="Da Vinci")
        Artist.objects.create(name="Monet")

        artists = Artist.objects.all()
        assert artists[0].name == "Da Vinci"
        assert artists[1].name == "Monet"
        assert artists[2].name == "Picasso"

    def test_artist_optional_fields(self):
        """Test la création d'un artiste avec des champs optionnels."""
        artist = Artist.objects.create(name="Artiste Inconnu")
        assert artist.birth_year is None
        assert artist.death_year is None
        assert artist.nationality == ""
        assert artist.biography == ""


# Tests pour le modèle Collection
@pytest.mark.django_db
class TestCollectionModel:

    def test_collection_creation(self, collection, user):
        """Test la création d'une collection."""
        assert collection.user == user
        assert collection.name == "Ma Collection"
        assert collection.description == "Une belle collection d'art"
        assert collection.created_at is not None

    def test_collection_str_method(self, collection):
        """Test la méthode __str__ de Collection."""
        assert str(collection) == "Ma Collection"

    def test_collection_user_relationship(self, user):
        """Test la relation avec l'utilisateur."""
        collection1 = Collection.objects.create(user=user, name="Collection 1")
        collection2 = Collection.objects.create(user=user, name="Collection 2")

        assert user.collections.count() == 2
        assert collection1 in user.collections.all()
        assert collection2 in user.collections.all()


# Tests pour le modèle Exhibition
@pytest.mark.django_db
class TestExhibitionModel:

    def test_exhibition_creation(self, exhibition, user):
        """Test la création d'une exposition."""
        assert exhibition.user == user
        assert exhibition.name == "Exposition Renaissance"
        assert exhibition.location == "Musée du Louvre"
        assert exhibition.start_date == date(2023, 1, 1)
        assert exhibition.end_date == date(2023, 12, 31)
        assert exhibition.description == "Une exposition sur la Renaissance"
        assert exhibition.created_at is not None

    def test_exhibition_str_method(self, exhibition):
        """Test la méthode __str__ de Exhibition."""
        assert str(exhibition) == "Exposition Renaissance"

    def test_exhibition_ordering(self, user):
        """Test l'ordre par défaut des expositions (par date de début décroissante)."""
        Exhibition.objects.create(user=user, name="Expo 1", start_date=date(2023, 1, 1))
        Exhibition.objects.create(user=user, name="Expo 2", start_date=date(2023, 6, 1))
        Exhibition.objects.create(user=user, name="Expo 3", start_date=date(2023, 3, 1))

        exhibitions = Exhibition.objects.all()
        assert exhibitions[0].name == "Expo 2"  # Date la plus récente
        assert exhibitions[1].name == "Expo 3"
        assert exhibitions[2].name == "Expo 1"


# Tests pour les modèles simples (ArtType, Support, Technique, Keyword)
@pytest.mark.django_db
class TestSimpleModels:

    def test_art_type_creation(self, art_type):
        """Test la création d'un type d'art."""
        assert art_type.name == "Peinture"
        assert art_type.created_at is not None
        assert str(art_type) == "Peinture"

    def test_art_type_unique_constraint(self, art_type):
        """Test la contrainte d'unicité sur le nom du type d'art."""
        with pytest.raises(IntegrityError):
            ArtType.objects.create(name="Peinture")

    def test_support_creation(self, support):
        """Test la création d'un support."""
        assert support.name == "Toile"
        assert support.created_at is not None
        assert str(support) == "Toile"

    def test_support_unique_constraint(self, support):
        """Test la contrainte d'unicité sur le nom du support."""
        with pytest.raises(IntegrityError):
            Support.objects.create(name="Toile")

    def test_technique_creation(self, technique):
        """Test la création d'une technique."""
        assert technique.name == "Huile sur toile"
        assert technique.created_at is not None
        assert str(technique) == "Huile sur toile"

    def test_technique_unique_constraint(self, technique):
        """Test la contrainte d'unicité sur le nom de la technique."""
        with pytest.raises(IntegrityError):
            Technique.objects.create(name="Huile sur toile")

    def test_keyword_creation(self, keyword):
        """Test la création d'un mot-clé."""
        assert keyword.name == "Renaissance"
        assert keyword.created_at is not None
        assert str(keyword) == "Renaissance"

    def test_keyword_unique_constraint(self, keyword):
        """Test la contrainte d'unicité sur le nom du mot-clé."""
        with pytest.raises(IntegrityError):
            Keyword.objects.create(name="Renaissance")


# Tests pour le modèle Artwork
@pytest.mark.django_db
class TestArtworkModel:

    def test_artwork_creation(self, artwork, user, artist):
        """Test la création d'une œuvre d'art."""
        assert artwork.user == user
        assert artwork.title == "Mona Lisa"
        assert artwork.artists.count() == 1
        assert artwork.artists.first() == artist
        assert artwork.creation_year == 1503
        assert artwork.origin_country == "Italie"
        assert artwork.height == Decimal("77.00")
        assert artwork.width == Decimal("53.00")
        assert artwork.is_signed is True
        assert artwork.is_acquired is True
        assert artwork.current_location == "domicile"
        assert artwork.created_at is not None
        assert artwork.updated_at is not None

    def test_artwork_str_method_with_title(self, artwork):
        """Test la méthode __str__ avec un titre."""
        assert str(artwork) == "Mona Lisa"

    def test_artwork_str_method_without_title_with_artists(self, user, artist):
        """Test la méthode __str__ sans titre mais avec artistes."""
        artwork = Artwork.objects.create(user=user, title="")
        artwork.artists.add(artist)
        assert str(artwork) == "Œuvre de Leonardo da Vinci"

    def test_artwork_str_method_without_title_and_artists(self, user):
        """Test la méthode __str__ sans titre ni artistes."""
        artwork = Artwork.objects.create(user=user, title="")
        result = str(artwork)
        assert result.startswith("Œuvre #")
        assert len(result) == 15  # "Œuvre #" + 8 caractères de l'UUID

    def test_artwork_get_absolute_url(self, artwork):
        """Test la méthode get_absolute_url."""
        expected_url = f"/artworks/{artwork.id}/"
        assert artwork.get_absolute_url() == expected_url

    def test_artwork_get_artists_display(self, artwork, user):
        """Test la méthode get_artists_display."""
        # Avec un artiste
        assert artwork.get_artists_display() == "Leonardo da Vinci"

        # Avec plusieurs artistes
        artist2 = Artist.objects.create(name="Michel-Ange")
        artwork.artists.add(artist2)
        assert artwork.get_artists_display() == "Leonardo da Vinci, Michel-Ange"

        # Sans artiste
        artwork_no_artist = Artwork.objects.create(user=user, title="Test")
        assert artwork_no_artist.get_artists_display() == ""

    def test_artwork_get_dimensions_display(self, artwork, user):
        """Test la méthode get_dimensions_display."""
        # Avec hauteur et largeur (depth=0 n'est pas affiché car considéré comme falsy)
        expected = "H: 77.00cm x L: 53.00cm"
        assert artwork.get_dimensions_display() == expected

        # Avec toutes les dimensions non-nulles
        artwork_full = Artwork.objects.create(
            user=user,
            title="Test",
            height=Decimal("50.00"),
            width=Decimal("40.00"),
            depth=Decimal("10.00"),
        )
        assert (
            artwork_full.get_dimensions_display()
            == "H: 50.00cm x L: 40.00cm x P: 10.00cm"
        )

        # Avec seulement hauteur et largeur
        artwork_partial = Artwork.objects.create(
            user=user, title="Test", height=Decimal("50.00"), width=Decimal("40.00")
        )
        assert artwork_partial.get_dimensions_display() == "H: 50.00cm x L: 40.00cm"

        # Sans dimensions
        artwork_no_dim = Artwork.objects.create(user=user, title="Test")
        assert artwork_no_dim.get_dimensions_display() == "Non spécifiées"

    def test_artwork_many_to_many_relationships(
        self, artwork, collection, exhibition, keyword
    ):
        """Test les relations many-to-many."""
        artwork.collections.add(collection)
        artwork.exhibitions.add(exhibition)
        artwork.keywords.add(keyword)

        assert artwork.collections.count() == 1
        assert artwork.exhibitions.count() == 1
        assert artwork.keywords.count() == 1
        assert collection in artwork.collections.all()
        assert exhibition in artwork.exhibitions.all()
        assert keyword in artwork.keywords.all()

    def test_artwork_parent_relationship(self, user, artwork):
        """Test la relation parent-enfant entre œuvres."""
        child_artwork = Artwork.objects.create(
            user=user, title="Étude pour Mona Lisa", parent_artwork=artwork
        )
        assert child_artwork.parent_artwork == artwork

    def test_artwork_ordering(self, user):
        """Test l'ordre par défaut des œuvres (par date de création décroissante)."""
        # Les fixtures créent déjà une œuvre, on en crée deux autres
        Artwork.objects.create(user=user, title="Œuvre 2")
        Artwork.objects.create(user=user, title="Œuvre 3")

        artworks = Artwork.objects.all()
        # La plus récemment créée doit être en premier
        assert artworks[0].title == "Œuvre 3"


# Tests pour le modèle ArtworkPhoto
@pytest.mark.django_db
class TestArtworkPhotoModel:

    def test_artwork_photo_creation(self, artwork):
        """Test la création d'une photo d'œuvre."""
        photo = ArtworkPhoto.objects.create(
            artwork=artwork, caption="Vue de face", is_primary=True
        )
        assert photo.artwork == artwork
        assert photo.caption == "Vue de face"
        assert photo.is_primary is True
        assert photo.created_at is not None

    def test_artwork_photo_str_method(self, artwork):
        """Test la méthode __str__ de ArtworkPhoto."""
        photo = ArtworkPhoto.objects.create(artwork=artwork)
        assert str(photo) == f"Photo de {artwork}"

    def test_artwork_photo_primary_logic(self, artwork):
        """Test la logique de photo principale."""
        # Créer la première photo comme principale
        photo1 = ArtworkPhoto.objects.create(artwork=artwork, is_primary=True)
        assert photo1.is_primary is True

        # Créer une deuxième photo comme principale
        photo2 = ArtworkPhoto.objects.create(artwork=artwork, is_primary=True)

        # Recharger la première photo depuis la base de données
        photo1.refresh_from_db()

        # La première photo ne doit plus être principale
        assert photo1.is_primary is False
        assert photo2.is_primary is True

    def test_artwork_photo_ordering(self, artwork):
        """Test l'ordre des photos (principale d'abord, puis par date)."""
        ArtworkPhoto.objects.create(artwork=artwork, is_primary=False)
        photo2 = ArtworkPhoto.objects.create(artwork=artwork, is_primary=True)
        ArtworkPhoto.objects.create(artwork=artwork, is_primary=False)

        photos = list(ArtworkPhoto.objects.all())
        assert photos[0].id == photo2.id  # Photo principale en premier
        assert photos[0].is_primary is True
        # Les photos non-principales suivent l'ordre de création
        non_primary_photos = [p for p in photos if not p.is_primary]
        assert len(non_primary_photos) == 2


# Tests pour le modèle WishlistItem
@pytest.mark.django_db
class TestWishlistItemModel:

    def test_wishlist_item_creation(self, user):
        """Test la création d'un élément de liste de souhaits."""
        item = WishlistItem.objects.create(
            user=user,
            title="Starry Night",
            artist_name="Vincent van Gogh",
            estimated_price=Decimal("1000000.00"),
            priority=1,
            notes="Chef-d'œuvre impressionniste",
            source_url="https://example.com/starry-night",
        )
        assert item.user == user
        assert item.title == "Starry Night"
        assert item.artist_name == "Vincent van Gogh"
        assert item.estimated_price == Decimal("1000000.00")
        assert item.priority == 1
        assert item.notes == "Chef-d'œuvre impressionniste"
        assert item.source_url == "https://example.com/starry-night"
        assert item.created_at is not None

    def test_wishlist_item_str_method(self, user):
        """Test la méthode __str__ de WishlistItem."""
        item = WishlistItem.objects.create(user=user, title="Test Artwork")
        assert str(item) == "Test Artwork"

    def test_wishlist_item_default_priority(self, user):
        """Test la priorité par défaut."""
        item = WishlistItem.objects.create(user=user, title="Test")
        assert item.priority == 3  # Priorité basse par défaut

    def test_wishlist_item_ordering(self, user):
        """Test l'ordre des éléments (par priorité puis par date décroissante)."""
        item1 = WishlistItem.objects.create(user=user, title="Item 1", priority=3)
        item2 = WishlistItem.objects.create(user=user, title="Item 2", priority=1)
        item3 = WishlistItem.objects.create(user=user, title="Item 3", priority=2)

        items = WishlistItem.objects.all()
        assert items[0] == item2  # Priorité 1 (haute)
        assert items[1] == item3  # Priorité 2 (moyenne)
        assert items[2] == item1  # Priorité 3 (basse)

    def test_wishlist_item_user_relationship(self, user):
        """Test la relation avec l'utilisateur."""
        item1 = WishlistItem.objects.create(user=user, title="Item 1")
        item2 = WishlistItem.objects.create(user=user, title="Item 2")

        assert user.wishlist.count() == 2
        assert item1 in user.wishlist.all()
        assert item2 in user.wishlist.all()


# Tests d'intégration et cas particuliers
@pytest.mark.django_db
class TestIntegrationAndEdgeCases:

    def test_cascade_deletion_user(self, user, artwork):
        """Test la suppression en cascade quand un utilisateur est supprimé."""
        artwork_id = artwork.id
        user.delete()

        # L'œuvre doit être supprimée
        assert not Artwork.objects.filter(id=artwork_id).exists()

    def test_set_null_on_foreign_key_deletion(self, artwork, art_type):
        """Test SET_NULL quand une clé étrangère est supprimée."""
        art_type.delete()
        artwork.refresh_from_db()
        assert artwork.art_type is None

    def test_artwork_with_minimal_data(self, user):
        """Test la création d'une œuvre avec le minimum de données."""
        artwork = Artwork.objects.create(user=user)
        assert artwork.user == user
        assert artwork.title == ""
        assert artwork.is_acquired is True  # Valeur par défaut
        assert artwork.current_location == "domicile"  # Valeur par défaut

    def test_multiple_artists_on_artwork(self, user):
        """Test une œuvre avec plusieurs artistes."""
        artist1 = Artist.objects.create(name="Artiste 1")
        artist2 = Artist.objects.create(name="Artiste 2")
        artist3 = Artist.objects.create(name="Artiste 3")

        artwork = Artwork.objects.create(user=user, title="Œuvre collaborative")
        artwork.artists.add(artist1, artist2, artist3)

        assert artwork.artists.count() == 3
        assert artwork.get_artists_display() == "Artiste 1, Artiste 2, Artiste 3"

    def test_artwork_photo_multiple_primary_different_artworks(self, user):
        """Ensure photos on separate artworks can both be primary."""
        artwork1 = Artwork.objects.create(user=user, title="Œuvre 1")
        artwork2 = Artwork.objects.create(user=user, title="Œuvre 2")

        photo1 = ArtworkPhoto.objects.create(artwork=artwork1, is_primary=True)
        photo2 = ArtworkPhoto.objects.create(artwork=artwork2, is_primary=True)

        # Les deux photos peuvent être principales car sur des œuvres différentes
        assert photo1.is_primary is True
        assert photo2.is_primary is True

    def test_artwork_uuid_uniqueness(self, user):
        """Test que chaque œuvre a un UUID unique."""
        artwork1 = Artwork.objects.create(user=user, title="Œuvre 1")
        artwork2 = Artwork.objects.create(user=user, title="Œuvre 2")

        assert artwork1.id != artwork2.id
        assert str(artwork1.id) != str(artwork2.id)

    def test_artwork_choices_validation(self, user):
        """Test les choix prédéfinis pour current_location."""
        artwork = Artwork.objects.create(
            user=user, title="Test", current_location="pretee"
        )
        assert artwork.current_location == "pretee"

    def test_wishlist_priority_choices(self, user):
        """Test les choix de priorité pour WishlistItem."""
        item_high = WishlistItem.objects.create(user=user, title="High", priority=1)
        item_medium = WishlistItem.objects.create(user=user, title="Medium", priority=2)
        item_low = WishlistItem.objects.create(user=user, title="Low", priority=3)

        assert item_high.priority == 1
        assert item_medium.priority == 2
        assert item_low.priority == 3
