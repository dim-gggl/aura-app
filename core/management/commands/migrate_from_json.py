"""
Django management command to migrate data from JSON to PostgreSQL.

This command provides a Django interface for migrating data from JSON files
to the PostgreSQL database with the aura schema.

Usage:
    python manage.py migrate_from_json --file data_export.json
"""

import json
import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from artworks.models import (
    Artist,
    ArtType,
    Artwork,
    ArtworkAttachment,
    ArtworkPhoto,
    Collection,
    Exhibition,
    Support,
    Technique,
    WishlistItem,
)
from contacts.models import Contact

# Import models
from core.models import User, UserProfile
from notes.models import Note

# Setup logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command to migrate data from JSON to PostgreSQL.
    """

    help = "Migrate data from JSON file to PostgreSQL database"

    def add_arguments(self, parser):
        """
        Add command arguments.
        """
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Path to the JSON file containing the data to migrate",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without actually migrating data",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help=(
                "Clear existing data before migration "
                "(WARNING: this deletes every record)."
            ),
        )

    def handle(self, *args, **options):
        """
        Handle the migration command.
        """
        json_file = options["file"]
        dry_run = options["dry_run"]
        clear_data = options["clear"]

        # Validate JSON file exists
        if not Path(json_file).exists():
            raise CommandError(f"JSON file not found: {json_file}")

        self.stdout.write("🚀 Starting data migration from JSON to PostgreSQL...")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "🔍 DRY RUN MODE - No data will be actually migrated"
                )
            )

        if clear_data:
            if not dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠️  CLEARING EXISTING DATA - This will delete all data!"
                    )
                )
                confirm = input("Are you sure you want to continue? (yes/no): ")
                if confirm.lower() != "yes":
                    self.stdout.write("Migration cancelled.")
                    return
                self.clear_existing_data()
            else:
                self.stdout.write(
                    self.style.WARNING("🔍 DRY RUN: Would clear existing data")
                )

        # Load and migrate data
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if dry_run:
                self.analyze_data(data)
            else:
                self.migrate_data(data)

            self.stdout.write(
                self.style.SUCCESS("✅ Migration completed successfully!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Migration failed: {e}"))
            raise CommandError(f"Migration failed: {e}")

    def clear_existing_data(self):
        """
        Clear all existing data from the database.
        """
        self.stdout.write("🗑️  Clearing existing data...")

        with transaction.atomic():
            # Delete in reverse order of dependencies
            ArtworkPhoto._default_manager.all().delete()
            ArtworkAttachment._default_manager.all().delete()
            WishlistItem._default_manager.all().delete()
            Artwork._default_manager.all().delete()
            Collection._default_manager.all().delete()
            Exhibition._default_manager.all().delete()
            Artist._default_manager.all().delete()
            Contact._default_manager.all().delete()
            Note._default_manager.all().delete()
            UserProfile._default_manager.all().delete()
            User._default_manager.all().delete()
            ArtType._default_manager.all().delete()
            Support._default_manager.all().delete()
            Technique._default_manager.all().delete()

        self.stdout.write(self.style.SUCCESS("✅ Existing data cleared"))

    def analyze_data(self, data):
        """
        Analyze the data to be migrated (dry run).
        """
        self.stdout.write("📊 Analyzing data to be migrated...")

        stats = {
            "users": len(data.get("users", [])),
            "artists": len(data.get("artists", [])),
            "artworks": len(data.get("artworks", [])),
            "collections": len(data.get("collections", [])),
            "exhibitions": len(data.get("exhibitions", [])),
            "contacts": len(data.get("contacts", [])),
            "notes": len(data.get("notes", [])),
            "art_types": len(data.get("art_types", [])),
            "supports": len(data.get("supports", [])),
            "techniques": len(data.get("techniques", [])),
        }

        self.stdout.write("📈 Data analysis results:")
        for key, count in stats.items():
            self.stdout.write(f"  - {key.replace('_', ' ').title()}: {count}")

        total_records = sum(stats.values())
        self.stdout.write(f"\n📊 Total records to migrate: {total_records}")

    def migrate_data(self, data):
        """
        Migrate data from JSON to PostgreSQL.
        """
        migration_stats = {
            "users": 0,
            "artists": 0,
            "artworks": 0,
            "collections": 0,
            "exhibitions": 0,
            "contacts": 0,
            "notes": 0,
            "errors": 0,
        }

        # Migrate in dependency order
        self.migrate_art_types_supports_techniques(data)
        self.migrate_users(data.get("users", []), migration_stats)
        self.migrate_artists(data.get("artists", []), migration_stats)
        self.migrate_collections(data.get("collections", []), migration_stats)
        self.migrate_exhibitions(data.get("exhibitions", []), migration_stats)
        self.migrate_artworks(data.get("artworks", []), migration_stats)
        self.migrate_contacts(data.get("contacts", []), migration_stats)
        self.migrate_notes(data.get("notes", []), migration_stats)

        # Print migration statistics
        self.stdout.write("\n📊 Migration statistics:")
        for key, count in migration_stats.items():
            if key != "errors":
                self.stdout.write(f"  - {key.replace('_', ' ').title()}: {count}")

        if migration_stats["errors"] > 0:
            self.stdout.write(
                self.style.WARNING(f"  - Errors: {migration_stats['errors']}")
            )

    def migrate_art_types_supports_techniques(self, data):
        """
        Migrate art types, supports, and techniques.
        """
        self.stdout.write("🎨 Migrating art types, supports, and techniques...")

        # Migrate art types
        for art_type_name in data.get("art_types", []):
            ArtType._default_manager.get_or_create(name=art_type_name)

        # Migrate supports
        for support_name in data.get("supports", []):
            Support._default_manager.get_or_create(name=support_name)

        # Migrate techniques
        for technique_name in data.get("techniques", []):
            Technique._default_manager.get_or_create(name=technique_name)

    def migrate_users(self, users_data, stats):
        """
        Migrate users.
        """
        self.stdout.write("👥 Migrating users...")

        for user_data in users_data:
            try:
                with transaction.atomic():
                    user, created = User._default_manager.get_or_create(
                        username=user_data["username"],
                        defaults={
                            "email": user_data.get("email", ""),
                            "first_name": user_data.get("first_name", ""),
                            "last_name": user_data.get("last_name", ""),
                            "is_active": user_data.get("is_active", True),
                            "is_staff": user_data.get("is_staff", False),
                            "is_superuser": user_data.get("is_superuser", False),
                        },
                    )

                    if created:
                        stats["users"] += 1
                        # Create user profile
                        UserProfile.get_or_create_for_user(user)
            except Exception as exc:
                username = user_data.get("username", "unknown")
                message = f"Error migrating user {username}: {exc}"
                self.stdout.write(self.style.WARNING(message))
                stats["errors"] += 1

    def migrate_artists(self, artists_data, stats):
        """
        Migrate artists.
        """
        self.stdout.write("🎭 Migrating artists...")

        for artist_data in artists_data:
            try:
                with transaction.atomic():
                    artist, created = Artist._default_manager.get_or_create(
                        name=artist_data["name"],
                        defaults={
                            "birth_year": artist_data.get("birth_year"),
                            "death_year": artist_data.get("death_year"),
                            "nationality": artist_data.get("nationality", ""),
                            "biography": artist_data.get("biography", ""),
                        },
                    )

                    if created:
                        stats["artists"] += 1
            except Exception as exc:
                artist_name = artist_data.get("name", "unknown")
                message = f"Error migrating artist {artist_name}: {exc}"
                self.stdout.write(self.style.WARNING(message))
                stats["errors"] += 1

    def migrate_collections(self, collections_data, stats):
        """
        Migrate collections.
        """
        self.stdout.write("📚 Migrating collections...")

        for collection_data in collections_data:
            try:
                with transaction.atomic():
                    user = User._default_manager.get(username=collection_data["user"])
                    collection, created = Collection._default_manager.get_or_create(
                        user=user,
                        name=collection_data["name"],
                        defaults={
                            "description": collection_data.get("description", ""),
                        },
                    )

                    if created:
                        stats["collections"] += 1
            except Exception as exc:
                collection_name = collection_data.get("name", "unknown")
                message = f"Error migrating collection {collection_name}: {exc}"
                self.stdout.write(self.style.WARNING(message))
                stats["errors"] += 1

    def migrate_exhibitions(self, exhibitions_data, stats):
        """
        Migrate exhibitions.
        """
        self.stdout.write("🏛️ Migrating exhibitions...")

        for exhibition_data in exhibitions_data:
            try:
                with transaction.atomic():
                    user = User._default_manager.get(username=exhibition_data["user"])
                    exhibition, created = Exhibition._default_manager.get_or_create(
                        user=user,
                        name=exhibition_data["name"],
                        defaults={
                            "location": exhibition_data.get("location", ""),
                            "start_date": exhibition_data.get("start_date"),
                            "end_date": exhibition_data.get("end_date"),
                            "description": exhibition_data.get("description", ""),
                        },
                    )

                    if created:
                        stats["exhibitions"] += 1
            except Exception as exc:
                exhibition_name = exhibition_data.get("name", "unknown")
                message = f"Error migrating exhibition {exhibition_name}: {exc}"
                self.stdout.write(self.style.WARNING(message))
                stats["errors"] += 1

    def migrate_artworks(self, artworks_data, stats):
        """
        Migrate artworks.
        """
        self.stdout.write("🖼️ Migrating artworks...")

        for artwork_data in artworks_data:
            try:
                with transaction.atomic():
                    user = User._default_manager.get(username=artwork_data["user"])
                    artwork, created = Artwork._default_manager.get_or_create(
                        user=user,
                        title=artwork_data.get("title", ""),
                        defaults={
                            "creation_year": artwork_data.get("creation_year"),
                            "origin_country": artwork_data.get("origin_country", ""),
                            "height": artwork_data.get("height"),
                            "width": artwork_data.get("width"),
                            "depth": artwork_data.get("depth"),
                            "weight": artwork_data.get("weight"),
                            "acquisition_date": artwork_data.get("acquisition_date"),
                            "acquisition_place": artwork_data.get(
                                "acquisition_place", ""
                            ),
                            "price": artwork_data.get("price"),
                            "provenance": artwork_data.get("provenance", ""),
                            "is_framed": artwork_data.get("is_framed", False),
                            "is_borrowed": artwork_data.get("is_borrowed", False),
                            "is_signed": artwork_data.get("is_signed", False),
                            "is_acquired": artwork_data.get("is_acquired", True),
                            "current_location": artwork_data.get(
                                "current_location", "domicile"
                            ),
                            "owners": artwork_data.get("owners", ""),
                            "contextual_references": artwork_data.get(
                                "contextual_references", ""
                            ),
                            "notes": artwork_data.get("notes", ""),
                            "last_exhibited": artwork_data.get("last_exhibited"),
                        },
                    )

                    if created:
                        stats["artworks"] += 1

                        # Associate artists
                        for artist_name in artwork_data.get("artists", []):
                            try:
                                artist = Artist._default_manager.get(name=artist_name)
                                artwork.artists.add(artist)
                            except Artist.DoesNotExist:
                                pass

                        # Associate collections
                        for collection_name in artwork_data.get("collections", []):
                            try:
                                collection = Collection._default_manager.get(
                                    user=user, name=collection_name
                                )
                                artwork.collections.add(collection)
                            except Collection.DoesNotExist:
                                pass

                        # Associate exhibitions
                        for exhibition_name in artwork_data.get("exhibitions", []):
                            try:
                                exhibition = Exhibition._default_manager.get(
                                    user=user, name=exhibition_name
                                )
                                artwork.exhibitions.add(exhibition)
                            except Exhibition.DoesNotExist:
                                pass
            except Exception as exc:
                artwork_title = artwork_data.get("title", "unknown")
                message = f"Error migrating artwork {artwork_title}: {exc}"
                self.stdout.write(self.style.WARNING(message))
                stats["errors"] += 1

    def migrate_contacts(self, contacts_data, stats):
        """
        Migrate contacts.
        """
        self.stdout.write("📞 Migrating contacts...")

        for contact_data in contacts_data:
            try:
                with transaction.atomic():
                    user = User._default_manager.get(username=contact_data["user"])
                    contact, created = Contact._default_manager.get_or_create(
                        user=user,
                        name=contact_data["name"],
                        defaults={
                            "contact_type": contact_data.get("contact_type", "autre"),
                            "address": contact_data.get("address", ""),
                            "phone": contact_data.get("phone", ""),
                            "email": contact_data.get("email", ""),
                            "website": contact_data.get("website", ""),
                            "notes": contact_data.get("notes", ""),
                        },
                    )

                    if created:
                        stats["contacts"] += 1
            except Exception as exc:
                contact_name = contact_data.get("name", "unknown")
                message = f"Error migrating contact {contact_name}: {exc}"
                self.stdout.write(self.style.WARNING(message))
                stats["errors"] += 1

    def migrate_notes(self, notes_data, stats):
        """
        Migrate notes.
        """
        self.stdout.write("📝 Migrating notes...")

        for note_data in notes_data:
            try:
                with transaction.atomic():
                    user = User._default_manager.get(username=note_data["user"])
                    note, created = Note._default_manager.get_or_create(
                        user=user,
                        title=note_data["title"],
                        defaults={
                            "content": note_data.get("content", ""),
                            "is_favorite": note_data.get("is_favorite", False),
                        },
                    )

                    if created:
                        stats["notes"] += 1
            except Exception as exc:
                note_title = note_data.get("title", "unknown")
                message = f"Error migrating note {note_title}: {exc}"
                self.stdout.write(self.style.WARNING(message))
                stats["errors"] += 1
