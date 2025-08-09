"""
Django forms for the artworks application.

This module contains all form classes used for creating and editing artworks,
artists, collections, exhibitions, and related entities. Forms use django-crispy-forms
for enhanced styling and layout, and custom widgets for dynamic functionality.

The forms include:
- ArtworkForm: Complex form with multiple sections and custom keyword handling
- ArtistForm: Simple form for artist biographical information
- CollectionForm: Form for user collections
- ExhibitionForm: Form for exhibition details with date validation
- WishlistItemForm: Form for wishlist items with priority levels
- ArtworkPhotoForm/FormSet: Inline formset for managing artwork photos

All forms use Crispy Forms for consistent Bootstrap styling and responsive layouts.
"""

from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Row, Column, Submit, Div, HTML

from .models import (
    Artwork, Artist, Collection, Exhibition, ArtworkPhoto, WishlistItem, 
    ArtType, Support, Technique
)
from .widgets import SelectOrCreateWidget, SelectMultipleOrCreateWidget


class ArtworkForm(forms.ModelForm):
    """
    Comprehensive form for creating and editing artworks.
    
    This form handles all aspects of artwork data including basic information,
    dimensions, acquisition details, location, and relationships with other entities.
    Features dynamic widget integration.
    
    Key features:
    - Organized into logical fieldsets using Crispy Forms
    - SelectOrCreate widgets for dynamic entity creation
    - User-specific querysets for collections and exhibitions
    - Responsive layout with Bootstrap grid system
    """
    
    class Meta:
        model = Artwork
        # Exclude fields that are auto-managed or set programmatically
        exclude = ['user', 'id', 'created_at', 'updated_at']
        widgets = {
            # Date inputs with HTML5 date picker
            'acquisition_date': forms.DateInput(attrs={'type': 'date'}),
            'last_exhibited': forms.DateInput(attrs={'type': 'date'}),
            
            # Text areas with appropriate sizing
            'notes': forms.Textarea(attrs={'rows': 4}),
            'contextual_references': forms.Textarea(attrs={'rows': 3}),
            'provenance': forms.Textarea(attrs={'rows': 3}),
            
            # Dynamic widgets for related entities
            'artists': SelectMultipleOrCreateWidget(Artist, 'artworks:artist_create_ajax'),
            'art_type': SelectOrCreateWidget(ArtType, 'artworks:arttype_create_ajax'),
            'support': SelectOrCreateWidget(Support, 'artworks:support_create_ajax'),
            'technique': SelectOrCreateWidget(Technique, 'artworks:technique_create_ajax'),
            'collections': SelectMultipleOrCreateWidget(Collection, 'artworks:collection_create_ajax'),
            'exhibitions': SelectMultipleOrCreateWidget(Exhibition, 'artworks:exhibition_create_ajax'),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Initialize form with user-specific data and custom layout.
        
        Args:
            user: Current user for filtering collections and exhibitions
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit collections and exhibitions to current user only
        if user:
            self.fields['collections'].queryset = Collection.objects.filter(user=user)
            self.fields['exhibitions'].queryset = Exhibition.objects.filter(user=user)
            # Limit parent artwork choices to the user's own artworks
            if 'parent_artwork' in self.fields:
                self.fields['parent_artwork'].queryset = Artwork.objects.filter(user=user)
        
        
        # Set querysets
        # - Artists suggestions should be scoped to the current user's usage
        if user:
            self.fields['artists'].queryset = (
                Artist.objects.filter(artwork__user=user).distinct()
            )
        else:
            # No user context: do not expose global artists in suggestions
            self.fields['artists'].queryset = Artist.objects.none()
        # - Reference entities remain global/common
        self.fields['art_type'].queryset = ArtType.objects.all()
        self.fields['support'].queryset = Support.objects.all()
        self.fields['technique'].queryset = Technique.objects.all()
        self.fields['tags'].label = "Mots-clés"
        # Retirer l'aide basée sur les virgules; l'UI sera gérée via JS (Tom Select-like)
        self.fields['tags'].help_text = ""
        
        # Configure Crispy Forms helper for layout
        self.helper = FormHelper()
        self.helper.form_tag = False  # Template handles form tags
        self.helper.layout = Layout(
            # Basic artwork information
            Fieldset(
                'Informations générales',
                Row(
                    Column('title', css_class='form-group col-md-8 mb-0'),
                    Column('creation_year', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('artists', css_class='form-group col-md-6 mb-0'),
                    Column('origin_country', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('art_type', css_class='form-group col-md-4 mb-0'),
                    Column('support', css_class='form-group col-md-4 mb-0'),
                    Column('technique', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            
            # Physical characteristics
            Fieldset(
                'Dimensions et caractéristiques',
                Row(
                    Column('height', css_class='form-group col-md-3 mb-0'),
                    Column('width', css_class='form-group col-md-3 mb-0'),
                    Column('depth', css_class='form-group col-md-3 mb-0'),
                    Column('weight', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('is_signed', css_class='form-group col-md-4 mb-0'),
                    Column('is_framed', css_class='form-group col-md-4 mb-0'),
                    Column('is_acquired', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            
            # Acquisition and provenance
            Fieldset(
                'Acquisition et provenance',
                Row(
                    Column('acquisition_date', css_class='form-group col-md-4 mb-0'),
                    Column('acquisition_place', css_class='form-group col-md-4 mb-0'),
                    Column('price', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                'provenance',
                'owners',
            ),
            
            # Current status and location
            Fieldset(
                'Localisation et statut',
                Row(
                    Column('current_location', css_class='form-group col-md-6 mb-0'),
                    Column('is_borrowed', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('collections', css_class='form-group col-md-6 mb-0'),
                    Column('exhibitions', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'last_exhibited',
            ),
            
            # Additional information
            Fieldset(
                'Informations complémentaires',
                'parent_artwork',
                'tags',
                'contextual_references',
                'notes',
            ),
        )
    
    def save(self, commit=True):
        return super().save(commit=commit)


class ArtistForm(forms.ModelForm):
    """
    Form for creating and editing artist information.
    
    Simple form with biographical fields and responsive layout.
    All fields are optional except name.
    """
    
    class Meta:
        model = Artist
        fields = '__all__'
        widgets = {
            'biography': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form with Crispy Forms layout."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(
                Column('birth_year', css_class='form-group col-md-6 mb-0'),
                Column('death_year', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'nationality',
            'biography',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )


class CollectionForm(forms.ModelForm):
    """
    Form for creating and editing user collections.
    
    Simple form with name and description fields.
    User field is excluded as it's set programmatically.
    """
    
    class Meta:
        model = Collection
        exclude = ['user']  # User is set in the view
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form with Crispy Forms layout."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )


class ExhibitionForm(forms.ModelForm):
    """
    Form for creating and editing exhibitions.
    
    Includes date fields with HTML5 date pickers and validation
    to ensure end date is not before start date.
    """
    
    class Meta:
        model = Exhibition
        exclude = ['user']  # User is set in the view
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form with Crispy Forms layout."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', placeholder="Nom de l'exposition"),
            Field('location', placeholder="Lieu de l'exposition"),
            Row(
                Column('start_date', css_class='form-group col-md-6 mb-0'),
                Column('end_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Field('description', placeholder="Description de l'exposition"),
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )


class WishlistItemForm(forms.ModelForm):
    """
    Form for creating and editing wishlist items.
    
    Allows users to track artworks they want to acquire with
    priority levels and estimated pricing information.
    """
    
    class Meta:
        model = WishlistItem
        exclude = ['user']  # User is set in the view
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form with Crispy Forms layout."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            Row(
                Column('artist_name', css_class='form-group col-md-6 mb-0'),
                Column('estimated_price', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('priority', css_class='form-group col-md-6 mb-0'),
                Column('source_url', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'notes',
            Submit('submit', 'Ajouter', css_class='btn btn-primary')
        )


class ArtworkPhotoForm(forms.ModelForm):
    """
    Form for individual artwork photos within the photo formset.
    
    Handles image upload, caption, and primary photo designation.
    Used as part of the ArtworkPhotoFormSet for managing multiple photos.
    """
    
    class Meta:
        model = ArtworkPhoto
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form with Crispy Forms layout for inline display."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Used within a formset
        self.helper.layout = Layout(
            Row(
                Column('image', css_class='form-group col-md-6 mb-0'),
                Column('caption', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('is_primary', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
        )


# Inline formset for managing multiple photos per artwork
ArtworkPhotoFormSet = inlineformset_factory(
    Artwork,           # Parent model
    ArtworkPhoto,      # Child model
    form=ArtworkPhotoForm,
    extra=3,           # Number of empty forms to display
    can_delete=True    # Allow deletion of existing photos
)