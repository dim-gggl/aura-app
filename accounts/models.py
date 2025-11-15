"""
Models and signal handlers for the accounts application.

This module handles user account creation and management, including automatic
profile creation for new users. It uses Django signals to ensure that every
user gets a corresponding UserProfile when their account is created.

Key functionality:
- Automatic UserProfile creation via Django signals
- Seamless integration with the core User model
- Ensures data consistency between User and UserProfile models
"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create UserProfile for new users.

    This signal handler is triggered every time a User instance is saved.
    When a new user is created (created=True), it automatically creates
    a corresponding UserProfile with default settings.

    This ensures that:
    - Every user has a profile for storing preferences and extended data
    - No manual profile creation is required in registration views
    - The relationship between User and UserProfile is always consistent
    - New users get default theme and settings immediately

    Args:
        sender: The model class that sent the signal (User)
        instance: The actual User instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments from the signal

    Note:
        This signal only triggers on user creation, not on updates.
        Profile updates are handled separately through the profile management views.
    """
    if created:
        # Create a new UserProfile for the newly created user
        # Uses default values defined in the UserProfile model
        UserProfile.objects.create(user=instance)
