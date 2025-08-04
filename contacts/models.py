# Create your models here.
from django.db import models
# from django.contrib.auth.models import User
from core.models import User


class Contact(models.Model):
    CONTACT_TYPES = [
        ('galerie', 'Galerie'),
        ('musee', 'Musée'),
        ('collectionneur', 'Collectionneur'),
        ('expert', 'Expert'),
        ('restaurateur', 'Restaurateur'),
        ('transporteur', 'Transporteur'),
        ('assureur', 'Assureur'),
        ('autre', 'Autre'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=200, verbose_name="Nom")
    contact_type = models.CharField(max_length=50, choices=CONTACT_TYPES, verbose_name="Type")
    address = models.TextField(blank=True, verbose_name="Adresse")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Site web")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
    
    def __str__(self):
        return self.name
