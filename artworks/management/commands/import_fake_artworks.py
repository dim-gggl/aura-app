import json
import uuid
from decimal import Decimal, InvalidOperation
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from artworks.models import Artwork, Artist, Collection, Exhibition, ArtType, Support, Technique

User = get_user_model()


def to_decimal(value):
    """Convert incoming JSON numeric or string to Decimal or return None."""
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def to_date(value):
    """Parse YYYY-MM-DD dates or return None."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except Exception:
        return None


def get_by_pk_or_none(model, pk):
    """Fetch instance by primary key, returning None if not found/invalid."""
    if pk in (None, ""):
        return None
    try:
        return model.objects.filter(pk=pk).first()
    except Exception:
        return None


class Command(BaseCommand):
    """
    Import artworks from a JSON file without raising exceptions.

    - Assigns all artworks to the target username.
    - Skips or nullifies unresolved relations (artists, collections, exhibitions, parent).
    - Converts numeric/decimal/date fields safely.
    - Creates/updates Artwork by UUID (id).
    - Does second pass for M2M and parent relations.
    """

    help = "Importe les œuvres depuis un fichier JSON en tolérant les erreurs et sans lever d'exception."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="fake_artworks.json",
            help="Chemin du fichier JSON des œuvres (par défaut: fake_artworks.json).",
        )
        parser.add_argument(
            "--username",
            default="dim-gggl",
            help='Nom d’utilisateur auquel rattacher les œuvres (par défaut: "dim-gggl").',
        )

    def handle(self, *args, **options):
        path = options["path"]
        username = options["username"]

        # Ensure user exists
        user, _ = User.objects.get_or_create(username=username, defaults={"email": "", "password": ""})

        # Load JSON
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Impossible de lire le fichier JSON: {e}"))
            return

        if not isinstance(data, list):
            self.stdout.write(self.style.ERROR("Le JSON doit être une liste d'œuvres."))
            return

        created, updated, failed = 0, 0, 0
        id_to_artwork = {}

        # First pass: create/update Artwork without M2M or parent
        for item in data:
            try:
                art_uuid = None
                try:
                    art_uuid = uuid.UUID(str(item.get("id"))) if item.get("id") else uuid.uuid4()
                except Exception:
                    art_uuid = uuid.uuid4()

                defaults = dict(
                    user=user,
                    title=item.get("title") or "",
                    creation_year=item.get("creation_year"),
                    origin_country=(item.get("origin_country") or "")[:100],
                    art_type=get_by_pk_or_none(ArtType, item.get("art_type")),
                    support=get_by_pk_or_none(Support, item.get("support")),
                    technique=get_by_pk_or_none(Technique, item.get("technique")),
                    height=to_decimal(item.get("height")),
                    width=to_decimal(item.get("width")),
                    depth=to_decimal(item.get("depth")),
                    weight=to_decimal(item.get("weight")),
                    acquisition_date=to_date(item.get("acquisition_date")),
                    acquisition_place=(item.get("acquisition_place") or "")[:200],
                    price=to_decimal(item.get("price")),
                    provenance=item.get("provenance") or "",
                    is_framed=bool(item.get("is_framed")),
                    is_borrowed=bool(item.get("is_borrowed")),
                    is_signed=bool(item.get("is_signed")),
                    is_acquired=bool(item.get("is_acquired", True)),
                    current_location=item.get("current_location") or "domicile",
                    owners=item.get("owners") or "",
                    contextual_references=item.get("contextual_references") or "",
                    notes=item.get("notes") or "",
                    last_exhibited=to_date(item.get("last_exhibited")),
                )

                obj, was_created = Artwork.objects.update_or_create(id=art_uuid, defaults=defaults)
                id_to_artwork[str(art_uuid)] = obj
                created += 1 if was_created else 0
                updated += 0 if was_created else 1

            except Exception as e:
                failed += 1
                # Do not raise; continue
                self.stdout.write(self.style.WARNING(f"Échec création/mise à jour d’une œuvre: {e}"))

        # Second pass: set M2M and parent, tags
        for item in data:
            try:
                key = str(item.get("id")) if item.get("id") else None
                if not key:
                    # Try to find by title + user as a fallback (rare)
                    continue
                artwork = id_to_artwork.get(key) or Artwork.objects.filter(id=key).first()
                if not artwork:
                    continue

                # Artists
                artist_ids = item.get("artists") or []
                if isinstance(artist_ids, list) and artist_ids:
                    existing_artists = list(Artist.objects.filter(pk__in=artist_ids))
                    artwork.artists.set(existing_artists)

                # Collections
                col_ids = item.get("collections") or []
                if isinstance(col_ids, list) and col_ids:
                    existing_cols = list(Collection.objects.filter(pk__in=col_ids, user=user))
                    artwork.collections.set(existing_cols)

                # Exhibitions
                ex_ids = item.get("exhibitions") or []
                if isinstance(ex_ids, list) and ex_ids:
                    existing_exhs = list(Exhibition.objects.filter(pk__in=ex_ids, user=user))
                    artwork.exhibitions.set(existing_exhs)

                # Parent artwork
                parent_id = item.get("parent_artwork")
                if parent_id:
                    parent = id_to_artwork.get(str(parent_id)) or Artwork.objects.filter(id=parent_id).first()
                    if parent:
                        artwork.parent_artwork = parent
                        artwork.save(update_fields=["parent_artwork"])

                # Tags
                tags = item.get("tags") or []
                if isinstance(tags, list):
                    artwork.tags.set(tags, clear=True)

            except Exception as e:
                # Do not raise; continue
                self.stdout.write(self.style.WARNING(f"Échec associations pour une œuvre: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Terminé. Créées: {created}, mises à jour: {updated}, erreurs: {failed}."
            )
        )