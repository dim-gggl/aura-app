from django.core.management.base import BaseCommand
from artworks.models import ArtType, Support, Technique


class Command(BaseCommand):
    
    help = 'Peuple la base de données avec les types d\'art, supports et techniques de base'

    def handle(self, *args, **options):
        # Types d'art initiaux
        art_types = [
            'Peinture', 'Sculpture', 'Photographie', 'Gravure', 
            'Dessin', 'Bande dessinée', 'Illustration', 'Poésie', 'Autre'
        ]
        
        for art_type in art_types:
            ArtType.objects.get_or_create(name=art_type)
        
        # Supports initiaux
        supports = [
            'Toile', 'Papier', 'Bois', 'Métal', 'Verre', 'Céramique', 
            'Pierre', 'Textile', 'Plastique', 'Carton'
        ]
        
        for support in supports:
            Support.objects.get_or_create(name=support)
        
        # Techniques initiales
        techniques = [
            'Huile', 'Acrylique', 'Aquarelle', 'Pastel', 'Encre', 
            'Crayon', 'Fusain', 'Gouache', 'Tempera', 'Mixte'
        ]
        
        for technique in techniques:
            Technique.objects.get_or_create(name=technique)
        
        self.stdout.write(
            self.style.SUCCESS('Données initiales créées avec succès!')
        ) 