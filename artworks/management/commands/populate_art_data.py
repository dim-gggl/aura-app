from django.core.management.base import BaseCommand
from artworks.models import ArtType, Support, Technique
from setup.config import get_art_types, get_techniques, get_supports

class Command(BaseCommand):
    
    help = 'Peuple la base de données avec les types d\'art, supports et techniques de base'

    def handle(self, *args, **options):
        # Types d'art initiaux
        art_types = get_art_types()
        
        for art_type in art_types:
            ArtType.objects.get_or_create(name=art_type)
        
        # Supports initiaux
        supports = get_supports()
        
        for support in supports:
            Support.objects.get_or_create(name=support)
        
        # Techniques initiales
        techniques = get_techniques()
        
        for technique in techniques:
            Technique.objects.get_or_create(name=technique)
        
        self.stdout.write(
            self.style.SUCCESS('Données initiales créées avec succès!')
        ) 