from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_favorite', 'user', 'created_at', 'updated_at']
    list_filter = ['is_favorite', 'user', 'created_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'