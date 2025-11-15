"""
Django forms for the notes application.

This module provides form classes for creating and editing notes with
enhanced styling and user experience features. Forms use django-crispy-forms
for consistent Bootstrap styling and responsive layouts.

Key features:
- Clean and intuitive note editing interface
- Large content textarea for comfortable writing
- Favorite checkbox easily accessible
- Responsive layout for different screen sizes
- Crispy Forms integration for consistent styling
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms

from .models import Note


class NoteForm(forms.ModelForm):
    """
    Form for creating and editing notes.

    This form provides a clean interface for note management with:
    - Title field with responsive width
    - Favorite checkbox for easy access
    - Large content textarea for comfortable writing
    - Crispy Forms styling for consistent appearance

    The form layout is optimized for note-taking workflows with
    the title taking most of the width and the favorite checkbox
    easily accessible on the same row.

    Key features:
    - Responsive layout that works on all screen sizes
    - Large textarea (10 rows) for comfortable content editing
    - Favorite status easily toggleable during creation/editing
    - Clean, distraction-free interface for writing
    - Consistent styling with the rest of the application
    """

    class Meta:
        model = Note
        exclude = ["user"]  # User field is set programmatically in views
        widgets = {
            # Large textarea for comfortable content editing
            "content": forms.Textarea(
                attrs={
                    "rows": 10,
                    "placeholder": "Écrivez votre note ici...",
                    "class": "form-control",
                    "label": "Contenu",
                }
            ),
            # Enhanced title input
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Titre de la note",
                    "class": "form-control",
                    "label": "Titre",
                }
            ),
            # Styled checkbox for favorite status
            "is_favorite": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with Crispy Forms layout and styling.

        Sets up the responsive layout with title and favorite checkbox
        on the same row, followed by the content area and submit button.
        """
        super().__init__(*args, **kwargs)

        # Enhance field labels and help text
        self.fields["title"].help_text = "Donnez un titre descriptif à votre note"
        self.fields["content"].help_text = (
            "Contenu principal de la note (supporte le texte formaté)"
        )
        self.fields["is_favorite"].help_text = (
            "Marquer comme favori pour un accès rapide"
        )

        # Configure Crispy Forms helper
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Title and favorite checkbox row
            Row(
                Column("title", css_class="form-group col-md-10 mb-0"),
                Column(
                    "is_favorite",
                    css_class="form-group col-md-2 mb-0 d-flex align-items-center",
                ),
                css_class="form-row",
            ),
            # Content textarea (full width)
            "content",
            # Submit button
            Submit("submit", "Enregistrer", css_class="btn btn-primary"),
        )

    def clean_title(self):
        """
        Validate and clean the title field.

        Performs additional validation to ensure title is meaningful
        and follows content guidelines.

        Returns:
            str: Cleaned title

        Raises:
            ValidationError: If title doesn't meet requirements
        """
        title = self.cleaned_data.get("title")

        if title:
            # Strip whitespace and ensure minimum length
            title = title.strip()

            if len(title) < 3:
                raise forms.ValidationError(
                    "Le titre doit contenir au moins 3 caractères."
                )

            # Optional: Check for meaningful content (not just numbers/symbols)
            if not any(char.isalpha() for char in title):
                raise forms.ValidationError(
                    "Le titre doit contenir au moins une lettre."
                )

        return title

    def clean_content(self):
        """
        Validate and clean the content field.

        Ensures content is not empty and meets minimum requirements
        for a meaningful note.

        Returns:
            str: Cleaned content

        Raises:
            ValidationError: If content doesn't meet requirements
        """
        content = self.cleaned_data.get("content")

        if content:
            # Strip whitespace
            content = content.strip()

            # Ensure minimum content length
            if len(content) < 10:
                raise forms.ValidationError(
                    "Le contenu doit contenir au moins 10 caractères."
                )

        return content

    def save(self, commit=True):
        """
        Save the note with additional processing if needed.

        This method can be extended to perform additional processing
        on the note content, such as:
        - Text formatting or cleanup
        - Automatic tagging or categorization
        - Content analysis or metadata extraction

        Args:
            commit: Whether to save to database immediately

        Returns:
            Note: The saved note instance
        """
        note = super().save(commit=commit)

        # Additional processing could be added here:
        # - Auto-generate tags from content
        # - Analyze content for keywords
        # - Set default favorite status based on content

        return note
