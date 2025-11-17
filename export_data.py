#!/usr/bin/env python3
"""
Script d'export des données vers JSON pour Aura.

Ce script permet d'exporter les données depuis votre base de données existante
vers un fichier JSON qui peut ensuite être importé dans PostgreSQL.

Usage:
    python export_data.py --output data_export.json
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import django

from artworks.models import (
    Artist,
    ArtType,
    Artwork,
    Collection,
    Exhibition,
    Support,
    Technique,
)
from contacts.models import Contact
from core.models import User
from notes.models import Note

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aura_app.settings.dev")

django.setup()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("export.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DataExporter:
    """
    Classe pour exporter les données vers JSON.
    """

    def __init__(self):
        """
        Initialize the exporter.
        """
        self.export_stats = {
            "users": 0,
            "artists": 0,
            "artworks": 0,
            "collections": 0,
            "exhibitions": 0,
            "contacts": 0,
            "notes": 0,
            "art_types": 0,
            "supports": 0,
            "techniques": 0,
        }

    def serialize_model_to_dict(self, queryset, fields=None):
        """
        Sérialise un queryset en dictionnaire Python.

        Args:
            queryset: QuerySet à sérialiser
            fields: Liste des champs à inclure (optionnel)

        Returns:
            list: Liste de dictionnaires représentant les objets
        """
        data = []
        for obj in queryset:
            obj_dict = {}
            for field in obj._meta.fields:
                if fields and field.name not in fields:
                    continue

                value = getattr(obj, field.name)

                # Convertir les objets datetime en string
                if hasattr(value, "isoformat"):
                    value = value.isoformat()
                elif hasattr(value, "strftime"):
                    value = value.strftime("%Y-%m-%d")

                obj_dict[field.name] = value

            # Ajouter les relations many-to-many
            for field in obj._meta.many_to_many:
                if fields and field.name not in fields:
                    continue

                related_objects = getattr(obj, field.name).all()
                if field.name == "artists":
                    obj_dict[field.name] = [artist.name for artist in related_objects]
                elif field.name == "collections":
                    obj_dict[field.name] = [
                        collection.name for collection in related_objects
                    ]
                elif field.name == "exhibitions":
                    obj_dict[field.name] = [
                        exhibition.name for exhibition in related_objects
                    ]
                else:
                    obj_dict[field.name] = [
                        str(related_obj) for related_obj in related_objects
                    ]

            data.append(obj_dict)

        return data

    def export_users(self):
        """
        Exporte les utilisateurs.

        Returns:
            list: Liste des utilisateurs exportés
        """
        logger.info("Export des utilisateurs...")
        users = User.objects.all()
        users_data = self.serialize_model_to_dict(users)
        self.export_stats["users"] = len(users_data)
        logger.info(f"{len(users_data)} utilisateurs exportés")
        return users_data

    def export_artists(self):
        """
        Exporte les artistes.

        Returns:
            list: Liste des artistes exportés
        """
        logger.info("Export des artistes...")
        artists = Artist.objects.all()
        artists_data = self.serialize_model_to_dict(artists)
        self.export_stats["artists"] = len(artists_data)
        logger.info(f"{len(artists_data)} artistes exportés")
        return artists_data

    def export_art_types_supports_techniques(self):
        """
        Exporte les types d'art, supports et techniques.

        Returns:
            dict: Dictionnaire contenant les types d'art, supports et techniques
        """
        logger.info("Export des types d'art, supports et techniques...")

        art_types = [art_type.name for art_type in ArtType.objects.all()]
        supports = [support.name for support in Support.objects.all()]
        techniques = [technique.name for technique in Technique.objects.all()]

        self.export_stats["art_types"] = len(art_types)
        self.export_stats["supports"] = len(supports)
        self.export_stats["techniques"] = len(techniques)

        logger.info(f"{len(art_types)} types d'art exportés")
        logger.info(f"{len(supports)} supports exportés")
        logger.info(f"{len(techniques)} techniques exportées")

        return {"art_types": art_types, "supports": supports, "techniques": techniques}

    def export_collections(self):
        """
        Exporte les collections.

        Returns:
            list: Liste des collections exportées
        """
        logger.info("Export des collections...")
        collections = Collection.objects.all()
        collections_data = self.serialize_model_to_dict(collections)
        self.export_stats["collections"] = len(collections_data)
        logger.info(f"{len(collections_data)} collections exportées")
        return collections_data

    def export_exhibitions(self):
        """
        Exporte les expositions.

        Returns:
            list: Liste des expositions exportées
        """
        logger.info("Export des expositions...")
        exhibitions = Exhibition.objects.all()
        exhibitions_data = self.serialize_model_to_dict(exhibitions)
        self.export_stats["exhibitions"] = len(exhibitions_data)
        logger.info(f"{len(exhibitions_data)} expositions exportées")
        return exhibitions_data

    def export_artworks(self):
        """
        Exporte les œuvres d'art.

        Returns:
            list: Liste des œuvres d'art exportées
        """
        logger.info("Export des œuvres d'art...")
        artworks = Artwork.objects.all()
        artworks_data = self.serialize_model_to_dict(artworks)
        self.export_stats["artworks"] = len(artworks_data)
        logger.info(f"{len(artworks_data)} œuvres d'art exportées")
        return artworks_data

    def export_contacts(self):
        """
        Exporte les contacts.

        Returns:
            list: Liste des contacts exportés
        """
        logger.info("Export des contacts...")
        contacts = Contact.objects.all()
        contacts_data = self.serialize_model_to_dict(contacts)
        self.export_stats["contacts"] = len(contacts_data)
        logger.info(f"{len(contacts_data)} contacts exportés")
        return contacts_data

    def export_notes(self):
        """
        Exporte les notes.

        Returns:
            list: Liste des notes exportées
        """
        logger.info("Export des notes...")
        notes = Note.objects.all()
        notes_data = self.serialize_model_to_dict(notes)
        self.export_stats["notes"] = len(notes_data)
        logger.info(f"{len(notes_data)} notes exportées")
        return notes_data

    def export_all_data(self, output_file):
        """
        Exporte toutes les données vers un fichier JSON.

        Args:
            output_file: Chemin vers le fichier de sortie JSON
        """
        logger.info(f"Début de l'export vers {output_file}")

        # Collecter toutes les données
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Export des données Aura pour migration PostgreSQL",
            },
            "users": self.export_users(),
            "artists": self.export_artists(),
            "collections": self.export_collections(),
            "exhibitions": self.export_exhibitions(),
            "artworks": self.export_artworks(),
            "contacts": self.export_contacts(),
            "notes": self.export_notes(),
        }

        # Ajouter les types d'art, supports et techniques
        export_data.update(self.export_art_types_supports_techniques())

        # Sauvegarder vers le fichier JSON
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Export terminé avec succès: {output_file}")
            self.print_export_stats()

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            raise

    def print_export_stats(self):
        """
        Affiche les statistiques d'export.
        """
        logger.info("=== Statistiques d'export ===")
        logger.info(f"Utilisateurs exportés: {self.export_stats['users']}")
        logger.info(f"Artistes exportés: {self.export_stats['artists']}")
        logger.info(f"Œuvres d'art exportées: {self.export_stats['artworks']}")
        logger.info(f"Collections exportées: {self.export_stats['collections']}")
        logger.info(f"Expositions exportées: {self.export_stats['exhibitions']}")
        logger.info(f"Contacts exportés: {self.export_stats['contacts']}")
        logger.info(f"Notes exportées: {self.export_stats['notes']}")
        logger.info(f"Types d'art exportés: {self.export_stats['art_types']}")
        logger.info(f"Supports exportés: {self.export_stats['supports']}")
        logger.info(f"Techniques exportées: {self.export_stats['techniques']}")
        logger.info("=== Fin des statistiques ===")


def main():
    """
    Fonction principale du script d'export.
    """
    parser = argparse.ArgumentParser(description="Exporter les données Aura vers JSON")
    parser.add_argument(
        "--output",
        "-o",
        default="data_export.json",
        help="Fichier de sortie JSON (défaut: data_export.json)",
    )

    args = parser.parse_args()

    # Créer l'exporteur et exécuter l'export
    exporter = DataExporter()
    exporter.export_all_data(args.output)

    logger.info("Export terminé!")


if __name__ == "__main__":
    main()
