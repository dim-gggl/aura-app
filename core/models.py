"""
Core models for the Aura art collection management application.

This module defines the fundamental models that support the entire application,
including custom user models and user profile management. These models serve
as the foundation for authentication, user preferences, and theming throughout
the application.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    This model provides the foundation for user authentication and authorization
    throughout the application. It inherits all standard Django user fields
    (username, email, password, etc.) while allowing for future customization.
    
    The custom user model is essential for applications that may need to extend
    user functionality later, as changing the user model after initial migration
    is extremely difficult in Django.
    
    Attributes:
        Inherits all fields from AbstractUser:
        - username: Unique username for login
        - email: User's email address
        - first_name: User's first name
        - last_name: User's last name
        - is_active: Boolean indicating if account is active
        - is_staff: Boolean indicating if user can access admin
        - is_superuser: Boolean indicating if user has all permissions
        - date_joined: Timestamp when user account was created
        - last_login: Timestamp of user's last login
    
    Related Models:
        - UserProfile: One-to-one relationship for extended user data
        - Artwork: One-to-many relationship for user's artwork collection
        - Collection: One-to-many relationship for user's collections
        - Exhibition: One-to-many relationship for user's exhibitions
        - WishlistItem: One-to-many relationship for user's wishlist
    """
    
    def __str__(self):
        """
        Return string representation of the user.
        
        Returns:
            str: The user's username
        """
        return self.username


class UserProfile(models.Model):
    """
    Extended user profile model for additional user preferences and data.
    
    This model stores user-specific preferences and additional information
    that extends the basic User model. It uses a one-to-one relationship
    to maintain separation of concerns while providing extended functionality.
    
    Key features:
    - Theme selection for UI customization
    - Profile picture upload and management
    - Timestamps for profile tracking
    - Extensive theme choices for personalization
    
    The profile is automatically created when needed and provides a clean
    way to extend user data without modifying the core User model.
    """
    
    # Comprehensive theme choices for UI customization
    # Each theme provides a different visual experience for the user
    THEME_CHOICES = [
        ('elegant', 'Élégant'),           # Classic, refined appearance
        ('futuristic', 'Futuriste'),     # Modern, sci-fi inspired
        ('playful', 'Ludique'),          # Bright, fun colors
        ('minimal', 'Minimaliste'),      # Clean, simple design
        ('retro', 'Rétro'),              # Vintage-inspired styling
        ('nature', 'Nature'),            # Earth tones, organic feel
        ('ocean', 'Océan'),              # Blue tones, water-inspired
        ('gothic', 'Gothique'),          # Dark, dramatic styling
        ('sunset', 'Coucher de soleil'), # Warm, golden colors
        ('forest', 'Forêt'),             # Green tones, woodland feel
        ('desert', 'Désert'),            # Sandy, warm earth tones
        ('cyberpunk', 'Cyberpunk'),      # Neon, high-tech aesthetic
        ('steampunk', 'Steampunk'),      # Industrial, brass tones
        ('artdeco', 'Art Déco'),         # 1920s inspired design
        ('noir', 'Noir'),                # Black and white, dramatic
        ('pastel', 'Pastel'),            # Soft, muted colors
        ('solarized', 'Solarisé'),       # Developer-friendly color scheme
        ('vaporwave', 'Vaporwave'),      # 80s retro-futuristic aesthetic
    ]
    
    # One-to-one relationship with User model
    # CASCADE ensures profile is deleted when user is deleted
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        help_text="Associated user account"
    )
    
    # Theme selection for UI customization
    theme = models.CharField(
        max_length=20, 
        choices=THEME_CHOICES, 
        default='elegant',
        help_text="Visual theme for the user interface"
    )
    
    # Profile picture with organized upload path
    # Images are stored in 'profile_pictures/' directory
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        null=True, 
        blank=True,
        help_text="User's profile picture (optional)"
    )
    
    # Timestamps for tracking profile creation and updates
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the profile was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the profile was last updated"
    )
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']  # Newest profiles first
    
    def __str__(self):
        """
        Return string representation of the user profile.
        
        Returns:
            str: Formatted string showing associated username
        """
        return f"Profil de {self.user.username}"
    
    def get_display_name(self):
        """
        Get the best display name for the user.
        
        Returns the user's full name if available, otherwise falls back
        to username. Useful for displaying user names in templates.
        
        Returns:
            str: Full name or username
        """
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        elif self.user.first_name:
            return self.user.first_name
        else:
            return self.user.username
    
    def get_theme_display_name(self):
        """
        Get the display name for the selected theme.
        
        Returns:
            str: Human-readable theme name
        """
        return dict(self.THEME_CHOICES).get(self.theme, self.theme)
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """
        Get or create a profile for the given user.
        
        This class method ensures that every user has a profile,
        creating one with default values if it doesn't exist.
        
        Args:
            user: User instance to get/create profile for
            
        Returns:
            tuple: (UserProfile instance, created boolean)
        """
        profile, created = cls.objects.get_or_create(
            user=user,
            defaults={
                'theme': 'elegant'  # Default theme
            }
        )
        return profile, created