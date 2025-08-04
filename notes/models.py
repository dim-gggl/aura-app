# Create your models here.
from django.db import models
# from django.contrib.auth.models import User
from core.models import User

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    is_favorite = models.BooleanField(default=False, verbose_name="Favori")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Note"
        verbose_name_plural = "Notes"
    
    def __str__(self):
        return self.title
