"""
Django context processors for the core application.

Context processors are functions that add variables to the template context
for every request. This module provides global context variables that are
available in all templates throughout the application.

Key functionality:
- Theme management: Makes the current user's theme available in all templates
- Automatic profile creation: Creates user profiles when they don't exist
- Fallback handling: Provides sensible defaults for anonymous users
"""

from django.core.exceptions import ObjectDoesNotExist

def theme_context(request):
    """
    Add the current user's theme to the template context.
    
    This context processor makes the user's selected theme available in all
    templates as 'current_theme'. This enables dynamic theming throughout
    the application without requiring each view to explicitly pass theme data.
    
    Behavior:
    - For authenticated users: Returns their selected theme from UserProfile
    - For anonymous users: Returns the default theme ('artdeco')
    - Auto-creates UserProfile if it doesn't exist for authenticated users
    - Handles errors gracefully with fallback to default theme
    
    The theme value is used in templates to:
    - Set CSS classes for dynamic styling
    - Control color schemes and visual elements
    - Provide personalized user experiences
    
    Args:
        request: HTTP request object containing user information
        
    Returns:
        dict: Context dictionary with 'current_theme' key
        
    Example:
        In templates: <html data-theme="{{ current_theme }}">
        In CSS: [data-theme="artdeco"] { ... }
    """
    # Default theme for fallback situations
    default_theme = 'artdeco'

    # If a theme is stored in session (set after profile update), use it directly
    session_theme = request.session.get('current_theme')
    if session_theme:
        return {'current_theme': session_theme}

    # Check if user is authenticated
    if request.user.is_authenticated:
        try:
            # Attempt to get the user's profile
            # Note: profile is a OneToOneField that may not exist yet
            profile = request.user.profile

            if profile and profile.theme:
                # User has a profile with a theme set
                theme = profile.theme
            else:
                # Profile exists but no theme set, or profile doesn't exist
                # Import here to avoid circular imports
                from core.models import UserProfile

                # Create profile if it doesn't exist, or update existing one
                profile, created = UserProfile.objects.get_or_create(
                    user=request.user,
                    defaults={'theme': default_theme}
                )
                theme = profile.theme if profile.theme else default_theme

        except (AttributeError, ObjectDoesNotExist):
            # Handle case where user.profile relationship doesn't exist
            # This can happen during migrations or in test environments
            theme = default_theme
    else:
        # Anonymous user - use default theme
        theme = default_theme

    return {'current_theme': theme}