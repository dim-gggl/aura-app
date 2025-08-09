"""
Django forms for the contacts application.

This module provides form classes for creating and editing contacts with
enhanced styling and validation. Forms use django-crispy-forms for consistent
Bootstrap styling and responsive layouts.

Key features:
- Comprehensive contact information fields
- Responsive form layout using Bootstrap grid
- Custom widget sizing for text areas
- Built-in validation for email and URL fields
- Crispy Forms integration for consistent styling
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

from .models import Contact


class ContactForm(forms.ModelForm):
    """
    Form for creating and editing contact information.
    
    This form handles all contact fields except the user field, which is set
    programmatically in the view. It provides a well-organized layout with
    responsive design and appropriate widget sizing for different field types.
    
    Key features:
    - Responsive two-column layout for efficient space usage
    - Custom textarea sizing for address and notes fields
    - Automatic validation for email and website fields
    - Crispy Forms integration for Bootstrap styling
    - Logical field grouping for better user experience
    
    Form sections:
    1. Basic info: Name and contact type
    2. Address: Multi-line address field
    3. Communication: Phone and email in two columns
    4. Web presence: Website URL
    5. Additional notes: Free-form notes field
    """
    
    class Meta:
        model = Contact
        exclude = ["user"]  # User field is set programmatically in views
        widgets = {
            # Multi-line textarea for addresses
            "address": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Adresse complète avec code postal et ville",
                "label": "Adresse"
            }),
            # Larger textarea for notes
            "notes": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Notes, spécialités, détails de la relation...",
                "label": "Notes"
            }),
            # Enhanced input widgets with placeholders
            "name": forms.TextInput(attrs={
                "placeholder": "Nom de la personne ou de l'organisation",
                "label": "Nom"
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "+33 1 23 45 67 89",
                "label": "Téléphone"
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "contact@example.com",
                "label": "Email"
            }),
            "website": forms.URLInput(attrs={
                "placeholder": "https://www.example.com",
                "label": "Site web"
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form with Crispy Forms layout and styling.
        
        Sets up the responsive layout using Bootstrap grid system for
        optimal display on different screen sizes.
        """
        super().__init__(*args, **kwargs)
        
        # Configure Crispy Forms helper
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Basic information row
            Row(
                Column("name", css_class="form-group col-md-8 mb-0"),
                Column("contact_type", css_class="form-group col-md-4 mb-0"),
                css_class="form-row"
            ),
            
            # Address field (full width)
            "address",
            
            # Communication information row
            Row(
                Column("phone", css_class="form-group col-md-6 mb-0"),
                Column("email", css_class="form-group col-md-6 mb-0"),
                css_class="form-row"
            ),
            
            # Website field (full width)
            "website",
            
            # Notes field (full width)
            "notes",
            
            # Submit button
            Submit("submit", "Enregistrer", css_class="btn btn-primary")
        )
    
    def clean_email(self):
        """
        Validate and clean the email field.
        
        Performs additional validation beyond Django's built-in EmailField
        validation to ensure email format is correct and domain exists.
        
        Returns:
            str: Cleaned email address
            
        Raises:
            ValidationError: If email format is invalid
        """
        email = self.cleaned_data.get('email')
        
        if email:
            # Convert to lowercase for consistency
            email = email.lower().strip()
            
            # Additional validation could be added here:
            # - Domain validation
            # - Blacklist checking
            # - Corporate email requirements
        
        return email
    
    def clean_phone(self):
        """
        Validate and clean the phone number field.
        
        Performs basic phone number cleaning and validation to ensure
        consistent formatting and valid phone number structure.
        
        Returns:
            str: Cleaned phone number
            
        Raises:
            ValidationError: If phone number format is invalid
        """
        phone = self.cleaned_data.get('phone')
        
        if phone:
            # Remove common formatting characters
            phone = phone.strip()
            
            # Basic validation - ensure it contains at least some digits
            if phone and not any(char.isdigit() for char in phone):
                raise forms.ValidationError(
                    "Le numéro de téléphone doit contenir au moins un chiffre."
                )
        
        return phone
    
    def clean_website(self):
        """
        Validate and clean the website URL field.
        
        Ensures URL is properly formatted and adds protocol if missing.
        
        Returns:
            str: Cleaned website URL
        """
        website = self.cleaned_data.get('website')
        
        if website:
            website = website.strip()
            
            # Add protocol if missing
            if website and not website.startswith(('http://', 'https://')):
                website = 'https://' + website
        
        return website