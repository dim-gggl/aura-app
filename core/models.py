from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    THEME_CHOICES = [
        ('elegant', 'Élégant'),
        ('futuristic', 'Futuriste'),
        ('playful', 'Ludique'),
        ('minimal', 'Minimaliste'),
        ('retro', 'Rétro'),
        ('nature', 'Nature'),
        ('ocean', 'Océan'),
        ('gothic', 'Gothique'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='elegant')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"