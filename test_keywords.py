#!/usr/bin/env python
"""
Script de test pour vérifier le fonctionnement des mots-clés
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aura_app.settings')
django.setup()

from artworks.models import Artwork, Keyword

def test_keywords():
    """Test des mots-clés"""
    print("Test des mots-clés...")
    
    # Récupérer une œuvre avec des mots-clés
    artworks = Artwork.objects.prefetch_related('keywords').all()
    
    if artworks.exists():
        artwork = artworks.first()
        print(f"Œuvre trouvée : {artwork.title}")
        
        # Test de la relation keywords
        print(f"Type de artwork.keywords : {type(artwork.keywords)}")
        print(f"artwork.keywords.exists() : {artwork.keywords.exists()}")
        
        if artwork.keywords.exists():
            print("Mots-clés trouvés :")
            for keyword in artwork.keywords.all():
                print(f"  - {keyword}")
        else:
            print("Aucun mot-clé trouvé")
            
        # Test de l'itération
        try:
            keywords_list = list(artwork.keywords.all())
            print(f"Nombre de mots-clés : {len(keywords_list)}")
        except Exception as e:
            print(f"Erreur lors de l'itération : {e}")
    else:
        print("Aucune œuvre trouvée")
    
    print("\nTest terminé !")

if __name__ == '__main__':
    test_keywords()
