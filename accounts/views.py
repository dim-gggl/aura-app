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

from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.contrib.auth import logout as logout_user
from django.utils.translation import gettext_lazy as _

from core.models import UserProfile

from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm


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
    if request.method == "POST":
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
            messages.success(request, _("Compte créé avec succès. Bienvenue!"))
            return redirect("core:dashboard")
    else:
        # GET request - display empty registration form
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


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
        defaults={"theme": "elegant"},  # Default theme for new profiles
    )

    if request.method == "POST":
        submitted_form = request.POST.get("form", "profile")

        if submitted_form == "password":
            # Changement de mot de passe
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            user_form = UserUpdateForm(instance=request.user)
            profile_form = UserProfileForm(instance=profile, user=request.user)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _("Votre mot de passe a été modifié."))
                return redirect("accounts:profile")
        else:
            # Mise à jour infos personnelles + préférences (thème, photo)
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(
                request.POST,
                request.FILES,
                instance=profile,
                user=request.user,
            )

            if user_form.is_valid() and profile_form.is_valid():
                # Suppression éventuelle de la photo
                if request.POST.get("remove_picture"):
                    if profile.profile_picture:
                        profile.profile_picture.delete(save=False)
                    profile.profile_picture = None

                user_form.save()
                updated_profile = profile_form.save()
                request.session["current_theme"] = updated_profile.theme
                messages.success(request, _("Profil mis à jour avec succès."))
                return redirect("accounts:profile")

        # Si on arrive ici, au moins un des formulaires n'est pas valide
        # S'assurer que les trois formulaires existent pour le rendu
        if submitted_form != "password":
            password_form = PasswordChangeForm(user=request.user)
    else:
        # GET request - display current data in forms
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile, user=request.user)
        password_form = PasswordChangeForm(user=request.user)

    # Prepare context with forms and theme choices for template
    context = {
        "form": profile_form,  # conserver la clé existante utilisée par le template
        "user_form": user_form,
        "password_form": password_form,
        "theme_choices": UserProfile.THEME_CHOICES,
    }

    return render(request, "accounts/profile.html", context)


def logout(request):
    logout_user(request=request )
    return redirect("core:home")
