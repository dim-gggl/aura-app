"""
Django forms for user account management in the Aura application.

This module provides custom forms for user registration and profile management,
extending Django's built-in forms with additional fields and enhanced styling
using django-crispy-forms for consistent Bootstrap integration.

Key features:
- Enhanced user registration with required personal information
- Profile management with theme selection and picture upload
- Crispy Forms integration for consistent styling
- Custom validation and field handling
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from core.models import User, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """
    Enhanced user registration form with additional required fields.

    Extends Django's built-in UserCreationForm to include email and name fields
    as required information. This ensures all users provide essential information
    during registration for better user experience and communication.

    Additional fields:
    - email: Required email address for communication and account recovery
    - first_name: User's first name for personalization
    - last_name: User's last name for complete identification

    Features:
    - Crispy Forms integration for consistent Bootstrap styling
    - Custom field ordering and layout
    - Enhanced validation through Django's built-in mechanisms
    - Automatic user data population during save
    """

    # Additional required fields beyond username and passwords
    email = forms.EmailField(
        required=True,
        help_text="Adresse email pour la communication et la récupération de compte",
    )
    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=30,
        required=True,
        help_text="Prénom pour personnaliser votre expérience",
    )
    last_name = forms.CharField(
        label=_("Nom"),
        max_length=30,
        required=True,
        help_text="Nom de famille pour l'identification complète",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with Crispy Forms styling and layout.

        Sets up the form helper for consistent Bootstrap styling and
        defines the field order and submit button appearance.
        """
        super().__init__(*args, **kwargs)

        # Configure Crispy Forms helper
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("username", label=_("Nom d'utilisateur")),
            Field("first_name", label=_("Prénom")),
            Field("last_name", label=_("Nom")),
            Field("email", label=_("Email")),
            Field("password1", label=_("Mot de passe")),
            Field("password2", label=_("Confirmation du mot de passe")),
            Submit("submit", _("Créer le compte"), css_class="btn btn-primary"),
        )

    def save(self, commit=True):
        """
        Save the user with additional field data.

        Extends the parent save method to populate the additional fields
        (email, first_name, last_name) from the form data.

        Args:
            commit: Whether to save the user to the database immediately

        Returns:
            User: The created user instance
        """
        # Get the user instance without saving to database yet
        user = super().save(commit=False)

        # Populate additional fields from cleaned form data
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        # Save to database if commit is True
        if commit:
            user.save()

        return user


class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile information and preferences.

    This form handles the extended user data stored in the UserProfile model,
    including theme selection and profile picture management. It integrates
    seamlessly with the user account system to provide comprehensive profile
    management capabilities.

    Key features:
    - Theme selection from predefined choices
    - Profile picture upload with file type validation
    - Integration with Crispy Forms for consistent styling
    - Dynamic theme choice loading to ensure current options
    - File input optimization for image uploads
    """

    class Meta:
        model = UserProfile
        fields = ["theme", "profile_picture"]
        widgets = {
            # File input optimized for image uploads
            "profile_picture": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",  # Restrict to image files only
                    "help_text": _("Formats supportés: JPG, PNG, GIF"),
                }
            ),
            # Select widget with Bootstrap styling
            "theme": forms.Select(
                attrs={
                    "class": "form-select",
                    "help_text": _(
                        "Choisissez votre thème préféré pour personnaliser l'interface"
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with user context and dynamic theme choices.

        Args:
            user: The user instance for context (passed as kwarg)
        """
        # Extract user from kwargs for potential future use
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Force update of theme choices to ensure we have the latest options
        # This is important if theme choices are ever updated dynamically
        self.fields["theme"].choices = UserProfile.THEME_CHOICES

        # Configure Crispy Forms helper
        self.helper = FormHelper()
        self.helper.form_tag = False  # Template handles form tags
        self.helper.layout = Layout(
            "theme",
            "profile_picture",
            # Submit button is handled in the template for more flexibility
        )

    def clean_profile_picture(self):
        """
        Validate the uploaded profile picture.

        Performs additional validation on the uploaded image file to ensure
        it meets size and format requirements.

        Returns:
            File: The validated profile picture file

        Raises:
            ValidationError: If the file doesn't meet requirements
        """
        picture = self.cleaned_data.get("profile_picture")

        if picture:
            # Check file size (limit to 5MB)
            if picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    _("La taille de l'image ne doit pas dépasser 5MB.")
                )

            # Check file format by examining the file extension
            allowed_types = ["jpg", "jpeg", "png", "gif"]
            file_extension = picture.name.split(".")[-1].lower()
            allowed_types_display = ", ".join(allowed_types)

            if file_extension not in allowed_types:
                message = _(
                    "Unsupported file format. Use one of the following: %(allowed)s"
                ) % {"allowed": allowed_types_display}
                raise forms.ValidationError(message)

        return picture


class UserUpdateForm(forms.ModelForm):
    """
    Formulaire pour modifier les informations personnelles de l'utilisateur.

    Permet de mettre à jour le prénom, le nom et l'email sur la page profil.
    Le rendu est laissé au template, le helper crispy est configuré sans balises <form>.
    """

    email = forms.EmailField(
        required=False,
        label=_("Email"),
        help_text=_("Adresse email associée à votre compte"),
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Labels en français et classes bootstrap
        self.fields["first_name"].label = _("Prénom")
        self.fields["last_name"].label = _("Nom")

        for field_name in ["first_name", "last_name", "email"]:
            self.fields[field_name].widget.attrs.setdefault("class", "form-control")

        # Helper crispy sans <form>
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "first_name",
            "last_name",
            "email",
        )
