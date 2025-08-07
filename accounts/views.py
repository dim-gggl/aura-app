"""
Views for user account management in the Aura application.

This module handles user registration, authentication, and profile management.
It provides comprehensive user account functionality including custom registration,
profile editing with theme selection, and profile picture management.

Key features:
- Custom user registration with automatic profile creation
- Profile management with theme selection and picture upload
- Automatic login after registration
- Profile picture deletion functionality
- Comprehensive error handling and user feedback
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

from .forms import CustomUserCreationForm, UserProfileForm
from core.models import UserProfile


def register(request):
    """
    Handle user registration with automatic profile creation and login.
    
    This view manages the complete user registration process:
    - Displays registration form for GET requests
    - Processes form submission for POST requests
    - Creates UserProfile automatically for new users
    - Logs in the user immediately after successful registration
    - Redirects to dashboard with welcome message
    
    The automatic profile creation ensures every user has the extended
    profile data needed for theme preferences and other settings.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Registration form (GET) or redirect to dashboard (POST success)
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create the new user account
            user = form.save()
            
            # Create a UserProfile for the new user with default settings
            # Note: This might be redundant if the signal handler is working,
            # but provides a fallback to ensure profile creation
            UserProfile.objects.get_or_create(user=user)
            
            # Automatically log in the new user
            login(request, user)
            
            # Provide success feedback and redirect to main application
            messages.success(request, 'Compte créé avec succès. Bienvenue!')
            return redirect('core:dashboard')
    else:
        # GET request - display empty registration form
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """
    Handle user profile viewing and editing with comprehensive functionality.
    
    This view provides complete profile management including:
    - User information editing (name, email, etc.)
    - Theme selection from available options
    - Profile picture upload and management
    - Profile picture deletion functionality
    - Automatic profile creation if it doesn't exist
    
    Features:
    - Handles both user data and profile data in a single form
    - Supports profile picture upload with file handling
    - Provides option to remove existing profile pictures
    - Includes all theme choices for selection
    - Comprehensive error handling and user feedback
    
    Args:
        request: HTTP request object (from authenticated user)
        
    Returns:
        HttpResponse: Profile form (GET) or redirect after successful update (POST)
    """
    # Ensure the user has a profile, create one with defaults if not
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'theme': 'elegant'}  # Default theme for new profiles
    )

    if request.method == 'POST':
        # Process profile update form
        form = UserProfileForm(
            request.POST, 
            request.FILES,  # Include files for profile picture upload
            instance=profile, 
            user=request.user
        )
        
        if form.is_valid():
            # Handle profile picture removal if requested
            if request.POST.get('remove_picture'):
                if profile.profile_picture:
                    # Delete the actual file from storage
                    profile.profile_picture.delete(save=False)
                # Clear the profile picture field
                profile.profile_picture = None
            
            # Save the form data
            form.save()
            
            # Provide success feedback
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('accounts:profile')
    else:
        # GET request - display current profile data in form
        form = UserProfileForm(instance=profile, user=request.user)
    
    # Prepare context with form and theme choices for template
    context = {
        'form': form,
        'theme_choices': UserProfile.THEME_CHOICES,  # All available themes
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_test(request):
    """
    Test/debug version of the profile view with enhanced debugging.
    
    This view is identical to the main profile view but includes additional
    debugging output for development and troubleshooting purposes. It uses
    a simplified template and provides console output for form validation.
    
    Debug features:
    - Prints POST and FILES data to console
    - Shows form validation status and errors
    - Uses simplified template for testing
    
    Args:
        request: HTTP request object (from authenticated user)
        
    Returns:
        HttpResponse: Simple profile form or redirect after update
        
    Note:
        This view should be removed or disabled in production environments
        as it exposes potentially sensitive debugging information.
    """
    # Ensure the user has a profile, create one if not
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=profile, 
            user=request.user
        )
        
        # Debug output for development
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        
        if form.is_valid():
            # Handle profile picture removal
            if request.POST.get('remove_picture'):
                if profile.profile_picture:
                    profile.profile_picture.delete(save=False)
                profile.profile_picture = None
            
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('accounts:profile_test')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    return render(request, 'accounts/profile_simple.html', {'form': form})