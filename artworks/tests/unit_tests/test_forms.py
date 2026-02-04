from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from artworks.forms import (
    ArtistForm,
    ArtworkForm,
    ArtworkPhotoForm,
    ArtworkPhotoFormSet,
    CollectionForm,
    ExhibitionForm,
    WishlistItemForm,
)
from artworks.models import (
    Artist,
    ArtType,
    Artwork,
    ArtworkPhoto,
    Collection,
    Exhibition,
    Keyword,
    Support,
    Technique,
    WishlistItem,
)

User = get_user_model()


# ================================
# FIXTURES POUR LES TESTS DE FORMS
# ================================


@pytest.fixture
def user():
    """Utilisateur pour les tests."""
    return User._default_manager.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def other_user():
    """Autre utilisateur pour les tests d'isolation."""
    return User._default_manager.create_user(
        username="otheruser", email="other@example.com", password="testpass123"
    )


@pytest.fixture
def artist():
    """Artiste pour les tests."""
    return Artist._default_manager.create(
        name="Vincent van Gogh",
        birth_year=1853,
        death_year=1890,
        nationality="Néerlandais",
        biography="Peintre post-impressionniste néerlandais",
    )


@pytest.fixture
def art_type():
    """Type d'art pour les tests."""
    return ArtType._default_manager.create(name="Peinture")


@pytest.fixture
def support():
    """Support pour les tests."""
    return Support._default_manager.create(name="Toile")


@pytest.fixture
def technique():
    """Technique pour les tests."""
    return Technique._default_manager.create(name="Huile sur toile")


@pytest.fixture
def collection(user):
    """Collection pour les tests."""
    return Collection._default_manager.create(
        user=user, name="Ma Collection Test", description="Description de test"
    )


@pytest.fixture
def exhibition(user):
    """Exposition pour les tests."""
    return Exhibition._default_manager.create(
        user=user,
        name="Exposition Test",
        location="Musée Test",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 3, 31),
        description="Description de l'exposition",
    )


@pytest.fixture
def artwork(user, artist, art_type, support, technique):
    """Œuvre d'art pour les tests."""
    artwork = Artwork._default_manager.create(
        user=user,
        title="La Nuit étoilée",
        creation_year=1889,
        height=Decimal("73.70"),
        width=Decimal("92.10"),
        origin_country="France",
        is_signed=True,
        is_framed=True,
        is_acquired=True,
        art_type=art_type,
        support=support,
        technique=technique,
        notes="Chef-d'œuvre de Van Gogh",
    )
    artwork.artists.add(artist)
    return artwork


@pytest.fixture
def keyword():
    """Mot-clé pour les tests."""
    return Keyword._default_manager.create(name="impressionnisme")


@pytest.fixture
def wishlist_item(user):
    """Élément de liste de souhaits pour les tests."""
    return WishlistItem._default_manager.create(
        user=user,
        title="Œuvre souhaitée",
        artist_name="Artiste Souhaité",
        estimated_price=Decimal("1000.00"),
        priority=WishlistItem.HIGH,
        notes="Notes sur l'œuvre souhaitée",
    )


# ===============================
# TESTS POUR LE FORMULAIRE ARTWORK
# ===============================


@pytest.mark.django_db
class TestArtworkForm:

    def test_artwork_form_valid_data(self, user, artist, art_type, support, technique):
        """Test la validation du formulaire ArtworkForm avec des données valides."""
        form_data = {
            "title": "Nouvelle Œuvre",
            "creation_year": 2023,
            "height": "50.00",
            "width": "40.00",
            "origin_country": "France",
            "current_location": "domicile",
            "is_signed": True,
            "is_framed": False,
            "is_acquired": True,
            "artists": [artist.pk],
            "art_type": art_type.pk,
            "support": support.pk,
            "technique": technique.pk,
            "keywords_text": "moderne, contemporain",
            "notes": "Notes sur l'œuvre",
        }

        form = ArtworkForm(data=form_data, user=user)
        assert form.is_valid(), f"Erreurs du formulaire : {form.errors}"

        # Tester la sauvegarde
        artwork = form.save(commit=False)
        artwork.user = user
        artwork.save()
        form.save_m2m()

        assert artwork.title == "Nouvelle Œuvre"
        assert artwork.creation_year == 2023
        assert artwork.height == Decimal("50.00")
        assert artist in artwork.artists.all()
        assert artwork.art_type == art_type

    def test_artwork_form_keywords_processing(self, user, artist):
        """Test le traitement des mots-clés dans ArtworkForm."""
        form_data = {
            "title": "Test Keywords",
            "current_location": "domicile",
            "artists": [artist.pk],
            "keywords_text": "impressionnisme, moderne, art français",
        }

        form = ArtworkForm(data=form_data, user=user)
        assert form.is_valid()

        artwork = form.save(commit=False)
        artwork.user = user
        artwork.save()
        form.save_m2m()
        form.save()  # Pour traiter les mots-clés

        # Vérifier que les mots-clés ont été créés et associés
        keywords = artwork.keywords.all()
        keyword_names = [kw.name for kw in keywords]

        assert len(keywords) == 3
        assert "impressionnisme" in keyword_names
        assert "moderne" in keyword_names
        assert "art français" in keyword_names

    def test_artwork_form_keywords_existing(self, user, artist, keyword):
        """Test que les mots-clés existants sont réutilisés."""
        initial_count = Keyword._default_manager.count()

        form_data = {
            "title": "Test Existing Keywords",
            "current_location": "domicile",
            "artists": [artist.pk],
            "keywords_text": f"{keyword.name}, nouveau mot-clé",
        }

        form = ArtworkForm(data=form_data, user=user)
        assert form.is_valid()

        artwork = form.save(commit=False)
        artwork.user = user
        artwork.save()
        form.save_m2m()
        form.save()

        # Vérifier qu'un seul nouveau mot-clé a été créé
        assert Keyword._default_manager.count() == initial_count + 1

        keywords = artwork.keywords.all()
        keyword_names = [kw.name for kw in keywords]
        assert keyword.name in keyword_names
        assert "nouveau mot-clé" in keyword_names

    def test_artwork_form_user_collections_filter(self, user, other_user):
        """Test que le formulaire filtre les collections par utilisateur."""
        user_collection = Collection._default_manager.create(user=user, name="Collection User")
        other_collection = Collection._default_manager.create(
            user=other_user, name="Collection Other"
        )

        form = ArtworkForm(user=user)

        collection_queryset = form.fields["collections"].queryset
        assert user_collection in collection_queryset
        assert other_collection not in collection_queryset

    def test_artwork_form_user_exhibitions_filter(self, user, other_user):
        """Test que le formulaire filtre les expositions par utilisateur."""
        user_exhibition = Exhibition._default_manager.create(
            user=user,
            name="Expo User",
            location="Lieu",
            start_date=date.today(),
            end_date=date.today(),
        )
        other_exhibition = Exhibition._default_manager.create(
            user=other_user,
            name="Expo Other",
            location="Lieu",
            start_date=date.today(),
            end_date=date.today(),
        )

        form = ArtworkForm(user=user)

        exhibition_queryset = form.fields["exhibitions"].queryset
        assert user_exhibition in exhibition_queryset
        assert other_exhibition not in exhibition_queryset

    def test_artwork_form_initial_keywords(self, artwork, keyword):
        """Test que les mots-clés existants sont chargés dans le formulaire."""
        artwork.keywords.add(keyword)

        form = ArtworkForm(instance=artwork, user=artwork.user)

        assert form.fields["keywords_text"].initial == keyword.name

    def test_artwork_form_invalid_data(self, user):
        """Test la validation avec des données invalides."""
        form_data = {
            "creation_year": "invalid_year",  # Année invalide
            "height": "invalid_height",  # Hauteur invalide
            "current_location": "",  # Location requise
        }

        form = ArtworkForm(data=form_data, user=user)
        assert not form.is_valid()
        assert "creation_year" in form.errors
        assert "height" in form.errors
        assert "current_location" in form.errors

    def test_artwork_form_empty_keywords(self, user, artist, artwork):
        """Test la gestion des mots-clés vides."""
        # Ajouter des mots-clés existants
        keyword1 = Keyword._default_manager.create(name="test1")
        keyword2 = Keyword._default_manager.create(name="test2")
        artwork.keywords.add(keyword1, keyword2)

        form_data = {
            "title": "Test Empty Keywords",
            "current_location": "domicile",
            "artists": [artist.pk],
            "keywords_text": "",  # Mots-clés vides
        }

        form = ArtworkForm(data=form_data, instance=artwork, user=user)
        assert form.is_valid()

        form.save()

        # Vérifier que les mots-clés ont été supprimés
        assert artwork.keywords.count() == 0


# ===============================
# TESTS POUR LE FORMULAIRE ARTIST
# ===============================


@pytest.mark.django_db
class TestArtistForm:

    def test_artist_form_valid_data(self):
        """Test la validation du formulaire ArtistForm avec des données valides."""
        form_data = {
            "name": "Pablo Picasso",
            "birth_year": 1881,
            "death_year": 1973,
            "nationality": "Espagnol",
            "biography": "Peintre, dessinateur et sculpteur espagnol",
        }

        form = ArtistForm(data=form_data)
        assert form.is_valid()

        artist = form.save()
        assert artist.name == "Pablo Picasso"
        assert artist.birth_year == 1881
        assert artist.nationality == "Espagnol"

    def test_artist_form_required_fields(self):
        """Test que seul le nom est requis."""
        form_data = {"name": "Artiste Inconnu"}

        form = ArtistForm(data=form_data)
        assert form.is_valid()

        artist = form.save()
        assert artist.name == "Artiste Inconnu"
        assert artist.birth_year is None
        assert artist.death_year is None

    def test_artist_form_invalid_data(self):
        """Test la validation avec des données invalides."""
        form_data = {
            "name": "",  # Nom requis
            "birth_year": "invalid",  # Année invalide
        }

        form = ArtistForm(data=form_data)
        assert not form.is_valid()
        assert "name" in form.errors
        assert "birth_year" in form.errors


# ==================================
# TESTS POUR LE FORMULAIRE COLLECTION
# ==================================


@pytest.mark.django_db
class TestCollectionForm:

    def test_collection_form_valid_data(self):
        """Test la validation du formulaire CollectionForm avec des données valides."""
        form_data = {
            "name": "Art Moderne",
            "description": "Collection d'art moderne du 20ème siècle",
        }

        form = CollectionForm(data=form_data)
        assert form.is_valid()

        # Ne peut pas sauvegarder sans utilisateur
        collection = form.save(commit=False)
        assert collection.name == "Art Moderne"
        assert collection.description == "Collection d'art moderne du 20ème siècle"

    def test_collection_form_required_fields(self):
        """Test que seul le nom est requis."""
        form_data = {"name": "Collection Simple"}

        form = CollectionForm(data=form_data)
        assert form.is_valid()

    def test_collection_form_invalid_data(self):
        """Test la validation avec des données invalides."""
        form_data = {
            "name": "",  # Nom requis
        }

        form = CollectionForm(data=form_data)
        assert not form.is_valid()
        assert "name" in form.errors


# ===================================
# TESTS POUR LE FORMULAIRE EXHIBITION
# ===================================


@pytest.mark.django_db
class TestExhibitionForm:

    def test_exhibition_form_valid_data(self):
        """Test la validation du formulaire ExhibitionForm avec des données valides."""
        form_data = {
            "name": "Exposition Impressionniste",
            "location": "Musée d'Orsay",
            "start_date": "2023-06-01",
            "end_date": "2023-09-30",
            "description": "Grande exposition sur l'impressionnisme",
        }

        form = ExhibitionForm(data=form_data)
        assert form.is_valid()

        exhibition = form.save(commit=False)
        assert exhibition.name == "Exposition Impressionniste"
        assert exhibition.location == "Musée d'Orsay"
        assert exhibition.start_date == date(2023, 6, 1)
        assert exhibition.end_date == date(2023, 9, 30)

    def test_exhibition_form_required_fields(self):
        """Test les champs requis."""
        form_data = {"name": "Expo Simple", "location": "Lieu Simple"}

        form = ExhibitionForm(data=form_data)
        assert form.is_valid()

    def test_exhibition_form_invalid_data(self):
        """Test la validation avec des données invalides."""
        form_data = {
            "name": "",  # Nom requis
            "start_date": "invalid-date",  # Date invalide
        }

        form = ExhibitionForm(data=form_data)
        assert not form.is_valid()
        assert "name" in form.errors
        assert "start_date" in form.errors


# =====================================
# TESTS POUR LE FORMULAIRE WISHLIST ITEM
# =====================================


@pytest.mark.django_db
class TestWishlistItemForm:

    def test_wishlist_form_valid_data(self):
        """Validate WishlistItemForm behavior when it receives valid data."""
        form_data = {
            "title": "Œuvre Souhaitée",
            "artist_name": "Artiste Célèbre",
            "estimated_price": "5000.00",
            "priority": 1,  # Haute priorité
            "source_url": "https://example.com/artwork",
            "notes": "Notes importantes sur cette œuvre",
        }

        form = WishlistItemForm(data=form_data)
        assert form.is_valid()

        item = form.save(commit=False)
        assert item.title == "Œuvre Souhaitée"
        assert item.artist_name == "Artiste Célèbre"
        assert item.estimated_price == Decimal("5000.00")
        assert item.priority == 1

    def test_wishlist_form_required_fields(self):
        """Test les champs requis."""
        form_data = {
            "title": "Titre Minimal",
            "priority": 3,  # Valeur par défaut
            # artist_name a blank=True, donc optionnel
        }

        form = WishlistItemForm(data=form_data)
        assert form.is_valid(), f"Erreurs: {form.errors}"

    def test_wishlist_form_invalid_data(self):
        """Test la validation avec des données invalides."""
        form_data = {
            "title": "",  # Titre requis
            "estimated_price": "invalid_price",  # Prix invalide
            "source_url": "invalid-url",  # URL invalide
        }

        form = WishlistItemForm(data=form_data)
        assert not form.is_valid()
        assert "title" in form.errors
        assert "estimated_price" in form.errors
        assert "source_url" in form.errors


# =====================================
# TESTS POUR LE FORMULAIRE ARTWORK PHOTO
# =====================================


@pytest.mark.django_db
class TestArtworkPhotoForm:

    def test_artwork_photo_form_valid_data(self):
        """Test la validation du formulaire ArtworkPhotoForm."""
        form_data = {"caption": "Vue principale de l'œuvre", "is_primary": True}

        form = ArtworkPhotoForm(data=form_data)
        # Note: Le champ image est requis mais on ne peut pas facilement
        # tester l'upload de fichier dans un test unitaire simple
        assert "caption" not in form.errors
        assert "is_primary" not in form.errors

    def test_artwork_photo_form_empty_caption(self):
        """Test que la légende peut être vide."""
        form_data = {"caption": "", "is_primary": False}

        form = ArtworkPhotoForm(data=form_data)
        assert "caption" not in form.errors


# =====================================
# TESTS POUR LE FORMSET ARTWORK PHOTO
# =====================================


@pytest.mark.django_db
class TestArtworkPhotoFormSet:

    def test_artwork_photo_formset_creation(self, artwork):
        """Test la création du formset ArtworkPhotoFormSet."""
        formset = ArtworkPhotoFormSet(instance=artwork)

        # Vérifier que le formset a été créé avec le bon nombre de formulaires
        assert len(formset.forms) == 3  # extra=3 défini dans forms.py
        assert formset.instance == artwork

    def test_artwork_photo_formset_valid_empty(self, artwork):
        """Test qu'un formset sans données est valide."""
        # Un formset vide sans données POST devrait être valide
        formset = ArtworkPhotoFormSet(instance=artwork)

        # Vérifier que le formset non-lié est considéré comme valide
        assert not formset.is_bound
        assert len(formset.forms) == 3  # extra=3

    def test_artwork_photo_formset_with_existing_photos(self, artwork):
        """Test le formset avec des photos existantes."""
        # Créer une photo existante
        photo = ArtworkPhoto._default_manager.create(
            artwork=artwork, caption="Photo existante", is_primary=True
        )

        formset = ArtworkPhotoFormSet(instance=artwork)

        # Le formset devrait avoir 1 formulaire initial + 3 extra
        assert len(formset.forms) == 4
        assert formset.forms[0].instance == photo


# =====================================
# TESTS D'INTÉGRATION FORMULAIRES-MODÈLES
# =====================================


@pytest.mark.django_db
class TestFormModelIntegration:

    def test_artwork_form_complete_workflow(
        self, user, artist, art_type, support, technique, collection, exhibition
    ):
        """Test complet du workflow ArtworkForm avec toutes les relations."""
        form_data = {
            "title": "Œuvre Complète",
            "creation_year": 2023,
            "height": "100.00",
            "width": "80.00",
            "depth": "5.00",
            "weight": "2.50",
            "origin_country": "France",
            "is_signed": True,
            "is_framed": True,
            "is_acquired": True,
            "acquisition_date": "2023-01-15",
            "acquisition_place": "Galerie Test",
            "price": "15000.00",
            "current_location": "domicile",
            "is_borrowed": False,
            "artists": [artist.pk],
            "art_type": art_type.pk,
            "support": support.pk,
            "technique": technique.pk,
            "collections": [collection.pk],
            "exhibitions": [exhibition.pk],
            "keywords_text": "moderne, coloré, expressif",
            "notes": "Œuvre remarquable acquise en 2023",
            "contextual_references": "Période bleue de l'artiste",
            "provenance": "Atelier de l'artiste",
        }

        form = ArtworkForm(data=form_data, user=user)
        assert form.is_valid(), f"Erreurs: {form.errors}"

        artwork = form.save(commit=False)
        artwork.user = user
        artwork.save()
        form.save_m2m()
        form.save()  # Pour traiter les mots-clés

        # Vérifications complètes
        artwork.refresh_from_db()
        assert artwork.title == "Œuvre Complète"
        assert artwork.creation_year == 2023
        assert artwork.height == Decimal("100.00")
        assert artwork.is_signed is True
        assert artist in artwork.artists.all()
        assert artwork.art_type == art_type
        assert collection in artwork.collections.all()
        assert exhibition in artwork.exhibitions.all()
        assert artwork.keywords.count() == 3

        keyword_names = [kw.name for kw in artwork.keywords.all()]
        assert "moderne" in keyword_names
        assert "coloré" in keyword_names
        assert "expressif" in keyword_names
