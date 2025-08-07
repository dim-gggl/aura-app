"""
Django models for the notes application.

This module defines the Note model for managing personal notes and documentation
within the art collection management system. Notes provide a flexible way for
users to record thoughts, research, observations, and other textual information
related to their art collection activities.

The Note model supports favorites functionality and maintains comprehensive
timestamps for tracking note creation and modification history.
"""

from django.db import models
from django.urls import reverse

from core.models import User


class Note(models.Model):
    """
    Model representing a user's personal note or documentation.
    
    Notes are flexible text-based records that users can create to document
    thoughts, research, observations, meeting notes, or any other textual
    information related to their art collection management activities.
    
    Key features:
    - User-specific data isolation for privacy
    - Favorite marking for quick access to important notes
    - Rich text content support through TextField
    - Automatic timestamps for creation and modification tracking
    - Flexible content structure for various note types
    
    Use cases:
    - Research notes about artists or artworks
    - Meeting notes with galleries, collectors, or experts
    - Personal observations and thoughts about pieces
    - Documentation of artwork condition or provenance
    - Exhibition planning and ideas
    - Market research and valuation notes
    - Conservation and care instructions
    """
    
    # === CORE FIELDS ===
    # User relationship for data isolation
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notes',
        help_text="Owner of this note"
    )
    
    # Note identification and content
    title = models.CharField(
        max_length=200, 
        verbose_name="Titre",
        help_text="Descriptive title for the note"
    )
    
    content = models.TextField(
        verbose_name="Contenu",
        help_text="Main content of the note (supports rich text)"
    )
    
    # === ORGANIZATION FEATURES ===
    # Favorite marking for quick access
    is_favorite = models.BooleanField(
        default=False, 
        verbose_name="Favori",
        help_text="Mark as favorite for quick access from dashboard"
    )
    
    # === METADATA ===
    # Automatic timestamps for tracking
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this note was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this note was last modified"
    )
    
    class Meta:
        ordering = ['-updated_at']  # Most recently updated first
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        
        # Optional: Add database indexes for performance
        indexes = [
            models.Index(fields=['user', '-updated_at']),  # User's recent notes
            models.Index(fields=['user', 'is_favorite']),  # User's favorite notes
        ]
    
    def __str__(self):
        """
        Return string representation of the note.
        
        Returns:
            str: Note title
        """
        return self.title
    
    def get_absolute_url(self):
        """
        Return the canonical URL for this note's detail view.
        
        Returns:
            str: URL path to note detail page
        """
        return reverse("notes:detail", kwargs={"pk": self.pk})
    
    def get_content_preview(self, length=100):
        """
        Get a truncated preview of the note content.
        
        Useful for displaying note previews in lists or cards without
        showing the full content.
        
        Args:
            length: Maximum length of the preview (default: 100)
            
        Returns:
            str: Truncated content with ellipsis if needed
        """
        if len(self.content) <= length:
            return self.content
        return self.content[:length].rsplit(' ', 1)[0] + '...'
    
    def get_word_count(self):
        """
        Get the word count of the note content.
        
        Returns:
            int: Number of words in the content
        """
        return len(self.content.split())
    
    def toggle_favorite(self):
        """
        Toggle the favorite status of this note.
        
        Convenience method for switching favorite status without
        requiring explicit save() call.
        
        Returns:
            bool: New favorite status
        """
        self.is_favorite = not self.is_favorite
        self.save(update_fields=['is_favorite', 'updated_at'])
        return self.is_favorite
    
    @classmethod
    def get_user_favorites(cls, user, limit=None):
        """
        Get a user's favorite notes, ordered by most recent update.
        
        Args:
            user: User instance
            limit: Optional limit on number of results
            
        Returns:
            QuerySet: User's favorite notes
        """
        queryset = cls.objects.filter(user=user, is_favorite=True)
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def get_recent_notes(cls, user, days=30, limit=10):
        """
        Get a user's recently updated notes within the specified timeframe.
        
        Args:
            user: User instance
            days: Number of days to look back (default: 30)
            limit: Maximum number of notes to return (default: 10)
            
        Returns:
            QuerySet: Recent notes within the timeframe
        """
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return cls.objects.filter(
            user=user,
            updated_at__gte=cutoff_date
        )[:limit]
    
    def is_recently_updated(self, hours=24):
        """
        Check if the note was updated recently.
        
        Args:
            hours: Number of hours to consider "recent" (default: 24)
            
        Returns:
            bool: True if note was updated within the specified timeframe
        """
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return self.updated_at >= cutoff_time