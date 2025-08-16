import json
import uuid
import os
from decimal import Decimal, InvalidOperation
from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from typing import Any, List, Optional

from artworks.models import (
    Artwork,
    Artist,
    Collection,
    Exhibition,
    ArtType,
    Support,
    Technique,
    LOCATIONS,
)
from setup.config import get_art_types, get_supports, get_techniques

User = get_user_model()

def to_decimal(value: Any) -> Optional[Decimal]:
    """Convert incoming JSON numeric or string to Decimal or return None."""
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def to_date(value: Any) -> Optional[date]:
    """Parse YYYY-MM-DD dates or return None."""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except Exception:
        return None


def resolve_reference(model, value: Any, names: List[str]):
    """
    Resolve a FK reference that may come as an index (1-based) or as a name.
    Returns the instance or None if cannot resolve.
    """
    if isinstance(value, int):
        if 1 <= value <= len(names):
            name = names[value - 1]
            obj, _ = model.objects.get_or_create(name=name)
            return obj
        return None
    if isinstance(value, str) and value.strip():
        obj, _ = model.objects.get_or_create(name=value.strip())
        return obj
    return None


class Command(BaseCommand):
    """
    Importe des œuvres factices depuis un fichier JSON et résout les références de façon portable.

    Rattache toutes les œuvres à l'utilisateur cible (créé si nécessaire),
    résout `art_type`/`support`/`technique` par index (1-based) ou par nom en
    s'appuyant sur `setup/*.json`, crée/récupère les artistes depuis
    `setup/fill_up/artists.json`, et gère les M2M en seconde passe.
    """

    help = "Importe des œuvres factices depuis un fichier JSON et résout les références de façon portable."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="setup/fill_up/fake_artworks.json",
            help="Chemin du fichier JSON des œuvres (défaut: setup/fill_up/fake_artworks.json)",
        )
        parser.add_argument(
            "--username",
            default="demo",
            help='Nom d’utilisateur auquel rattacher les œuvres (défaut: "demo")',
        )

    def handle(self, *args, **options):
        path = options.get("path")
        username = options.get("username")

        # Utilisateur cible (créé si nécessaire)
        user, _ = User.objects.get_or_create(username=username, defaults={"is_active": True})

        # Garantir la présence des référentiels
        art_type_names = list(get_art_types())
        support_names = list(get_supports())
        technique_names = list(get_techniques())
        for name in art_type_names:
            ArtType.objects.get_or_create(name=name)
        for name in support_names:
            Support.objects.get_or_create(name=name)
        for name in technique_names:
            Technique.objects.get_or_create(name=name)

        # Charger/constituer le catalogue d'artistes
        artists_catalog: List[Artist] = []
        artists_file = "setup/fill_up/artists.json"
        if os.path.exists(artists_file):
            try:
                with open(artists_file, "r", encoding="utf-8") as f:
                    artists_data = json.load(f) or []
                for a in artists_data:
                    name = (a.get("name") or "").strip()
                    if not name:
                        continue
                    artist, _ = Artist.objects.get_or_create(
                        name=name,
                        defaults={
                            "birth_year": a.get("birth_year"),
                            "death_year": a.get("death_year"),
                            "nationality": a.get("nationality") or "",
                            "biography": a.get("biography") or "",
                        },
                    )
                    artists_catalog.append(artist)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Impossible de charger les artistes de référence: {e}"))
        else:
            self.stdout.write(self.style.WARNING("Fichier d'artistes de référence introuvable; les œuvres seront importées sans artistes."))

        # Charger le JSON d'œuvres
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
        id_to_artwork: dict[str, Artwork] = {}

        # Première passe: création/màj (sans M2M ni parent)
        for item in data:
            try:
                try:
                    art_uuid = uuid.UUID(str(item.get("id"))) if item.get("id") else uuid.uuid4()
                except Exception:
                    art_uuid = uuid.uuid4()

                art_type_obj = resolve_reference(ArtType, item.get("art_type"), art_type_names)
                support_obj = resolve_reference(Support, item.get("support"), support_names)
                technique_obj = resolve_reference(Technique, item.get("technique"), technique_names)

                allowed_locations = {key for key, _ in LOCATIONS}
                current_location = item.get("current_location") or "domicile"
                if current_location not in allowed_locations:
                    current_location = "domicile"

                defaults = dict(
                    user=user,
                    title=item.get("title") or "",
                    creation_year=item.get("creation_year"),
                    origin_country=(item.get("origin_country") or "")[:100],
                    art_type=art_type_obj,
                    support=support_obj,
                    technique=technique_obj,
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
                    current_location=current_location,
                    owners=item.get("owners") or "",
                    contextual_references=item.get("contextual_references") or "",
                    notes=item.get("notes") or "",
                    last_exhibited=to_date(item.get("last_exhibited")),
                )

                obj, was_created = Artwork.objects.update_or_create(id=art_uuid, defaults=defaults)
                id_to_artwork[str(obj.id)] = obj
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                failed += 1
                self.stdout.write(self.style.WARNING(f"Échec création/mise à jour d’une œuvre: {e}"))

        # Seconde passe: M2M, parent, tags
        for item in data:
            try:
                key = str(item.get("id")) if item.get("id") else None
                if not key:
                    continue
                artwork = id_to_artwork.get(key) or Artwork.objects.filter(id=key).first()
                if not artwork:
                    continue

                # Artists via index (1-based)
                artists_indices = item.get("artists") or []
                artists_objs: List[Artist] = []
                if isinstance(artists_indices, list) and artists_indices and artists_catalog:
                    for idx in artists_indices:
                        if isinstance(idx, int) and 1 <= idx <= len(artists_catalog):
                            artists_objs.append(artists_catalog[idx - 1])
                if artists_objs:
                    artwork.artists.set(artists_objs)

                # Collections (créées si besoin) liées à l'utilisateur
                collections_values = item.get("collections") or []
                collections_objs: List[Collection] = []
                if isinstance(collections_values, list) and collections_values:
                    for val in collections_values:
                        name = None
                        if isinstance(val, int):
                            name = f"Collection {val}"
                        elif isinstance(val, str) and val.strip():
                            name = val.strip()
                        if name:
                            col, _ = Collection.objects.get_or_create(user=user, name=name)
                            collections_objs.append(col)
                if collections_objs:
                    artwork.collections.set(collections_objs)

                # Exhibitions (créées si besoin)
                exhibitions_values = item.get("exhibitions") or []
                exhibitions_objs: List[Exhibition] = []
                if isinstance(exhibitions_values, list) and exhibitions_values:
                    for val in exhibitions_values:
                        name = None
                        if isinstance(val, int):
                            name = f"Exposition {val}"
                        elif isinstance(val, str) and val.strip():
                            name = val.strip()
                        if name:
                            ex, _ = Exhibition.objects.get_or_create(user=user, name=name)
                            exhibitions_objs.append(ex)
                if exhibitions_objs:
                    artwork.exhibitions.set(exhibitions_objs)

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
                    artwork.tags.set([str(t) for t in tags], clear=True)

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Échec associations pour une œuvre: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Terminé. Créées: {created}, mises à jour: {updated}, erreurs: {failed}."
            )
        )

    