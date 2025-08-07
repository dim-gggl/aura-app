"""
Custom Django widgets for the artworks application.

This module provides enhanced form widgets that add dynamic functionality
to forms, allowing users to create new related entities on-the-fly without
leaving the current form. These widgets integrate with AJAX endpoints to
provide a seamless user experience.

Widgets included:
- SelectOrCreateWidget: Single selection with "add new" functionality
- SelectMultipleOrCreateWidget: Multiple selection with "add new" functionality  
- TagWidget: Text input with autocomplete for keywords/tags

All widgets require corresponding JavaScript functionality in select_or_create.js
to handle the dynamic behavior and AJAX communication.
"""

from django import forms
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe


class SelectOrCreateWidget(forms.Select):
    """
    Enhanced select widget that allows users to create new entities on-the-fly.
    
    This widget extends the standard Django Select widget by adding a button
    that opens a modal for creating new entities. When a new entity is created
    via AJAX, it's automatically added to the select options and selected.
    
    Usage:
        widget = SelectOrCreateWidget(Artist, 'artworks:artist_create_ajax')
    
    Attributes:
        model_class: The Django model class for the related entity
        create_url_name: URL name for the AJAX creation endpoint
    """
    
    def __init__(self, model_class, create_url_name, *args, **kwargs):
        """
        Initialize the widget with model class and creation URL.
        
        Args:
            model_class: Django model class (e.g., Artist, Collection)
            create_url_name: URL name for AJAX endpoint (e.g., 'artworks:artist_create_ajax')
        """
        self.model_class = model_class
        self.create_url_name = create_url_name
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the widget HTML including select element and add button.
        
        Args:
            name: Field name
            value: Current field value
            attrs: HTML attributes dictionary
            renderer: Django form renderer
            
        Returns:
            str: Safe HTML string containing the complete widget
        """
        if attrs is None:
            attrs = {}
        
        # Add CSS class and data attributes for JavaScript integration
        attrs["class"] = attrs.get("class", "") + " select-or-create"
        attrs["data-create-url"] = reverse_lazy(self.create_url_name)
        
        # Add a default "create new" option at the top
        choices = [("", "--- Sélectionner ou créer ---")] + list(self.choices)
        if hasattr(self, "queryset"):
            choices = [("", "--- Sélectionner ou créer ---")] + [
                (obj.pk, str(obj)) for obj in self.queryset
            ]
        
        # Render the standard select element
        select_html = super().render(name, value, attrs, renderer)
        
        # Add button for creating new entities
        add_button_html = f"""
        <button type="button" class="btn btn-sm btn-outline-primary add-new-btn" 
                data-field-name="{name}" 
                data-model-name="{self.model_class._meta.verbose_name}">
            + Ajouter un.e nouvel.le {self.model_class._meta.verbose_name.lower()}
        </button>
        """
        
        return mark_safe(f"<div class='select-or-create-wrapper'>{select_html}{add_button_html}</div>")


class SelectMultipleOrCreateWidget(forms.SelectMultiple):
    """
    Enhanced multiple select widget that allows users to create new entities on-the-fly.
    
    Similar to SelectOrCreateWidget but supports multiple selections. Users can
    select multiple existing entities and/or create new ones that are automatically
    added to the selection.
    
    Usage:
        widget = SelectMultipleOrCreateWidget(Artist, 'artworks:artist_create_ajax')
    
    Attributes:
        model_class: The Django model class for the related entity
        create_url_name: URL name for the AJAX creation endpoint
    """
    
    def __init__(self, model_class, create_url_name, *args, **kwargs):
        """
        Initialize the widget with model class and creation URL.
        
        Args:
            model_class: Django model class (e.g., Artist, Collection)
            create_url_name: URL name for AJAX endpoint
        """
        self.model_class = model_class
        self.create_url_name = create_url_name
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the widget HTML including multiple select element and add button.
        
        Args:
            name: Field name
            value: Current field value (list of selected IDs)
            attrs: HTML attributes dictionary
            renderer: Django form renderer
            
        Returns:
            str: Safe HTML string containing the complete widget
        """
        if attrs is None:
            attrs = {}
        
        # Add CSS classes and data attributes for JavaScript integration
        attrs["class"] = attrs.get("class", "") + " select-multiple-or-create"
        attrs["data-create-url"] = reverse_lazy(self.create_url_name)
        attrs["multiple"] = True  # Ensure multiple selection is enabled
        
        # Render the standard multiple select element
        select_html = super().render(name, value, attrs, renderer)
        
        # Add button for creating new entities
        add_button_html = f"""
        <button type="button" class="btn btn-sm btn-outline-primary add-new-multiple-btn" 
                data-field-name="{name}" 
                data-model-name="{self.model_class._meta.verbose_name}">
            + Ajouter un.e nouvel.le {self.model_class._meta.verbose_name.lower()}
        </button>
        """
        
        return mark_safe(f"<div class='select-multiple-or-create-wrapper'>{select_html}{add_button_html}</div>")


class TagWidget(forms.TextInput):
    """
    Enhanced text input widget for keyword/tag management with autocomplete.
    
    This widget provides an intelligent text input for managing keywords:
    - Autocomplete suggestions based on existing keywords
    - Ability to create new keywords on-the-fly
    - Comma-separated input for multiple keywords
    - Real-time suggestions dropdown
    
    The widget integrates with keyword autocomplete and creation AJAX endpoints
    to provide a smooth user experience for tag management.
    
    Usage:
        widget = TagWidget()
    
    Features:
        - Real-time autocomplete as user types
        - Dropdown suggestions with existing keywords
        - Automatic keyword creation for new terms
        - Comma-separated multi-keyword input
        - Responsive dropdown positioning
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the tag widget with autocomplete functionality.
        
        Sets up CSS classes and data attributes needed for JavaScript
        integration with autocomplete and creation endpoints.
        """
        super().__init__(*args, **kwargs)
        self.attrs.update({
            "class": "form-control keyword-input",
            # URL for fetching autocomplete suggestions
            "data-autocomplete-url": reverse_lazy("artworks:keyword_autocomplete"),
            # URL for creating new keywords via AJAX
            "data-create-url": reverse_lazy("artworks:keyword_create_ajax"),
            "placeholder": "Commencez à taper pour voir les suggestions..."
        })
    
    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the tag input widget with autocomplete dropdown container.
        
        Handles various input value formats (ManyToMany querysets, lists, strings)
        and converts them to comma-separated strings for display.
        
        Args:
            name: Field name
            value: Current field value (can be queryset, list, or string)
            attrs: HTML attributes dictionary
            renderer: Django form renderer
            
        Returns:
            str: Safe HTML string with input field and suggestions container
        """
        if attrs is None:
            attrs = {}
        
        # Handle different value types from Django forms
        if hasattr(value, "all"):
            # ManyToMany queryset - convert to comma-separated string
            value = ", ".join([kw.name for kw in value.all()])
        elif isinstance(value, list):
            # List of objects or strings
            value = ", ".join([str(v) for v in value])
        
        # Merge widget attributes with provided attributes
        attrs.update(self.attrs)
        
        # Render the standard text input
        input_html = super().render(name, value, attrs, renderer)
        
        # Add container for autocomplete suggestions dropdown
        suggestions_html = """
        <div class="keyword-suggestions" style="display: none;">
            <ul class="list-group position-absolute w-100" style="z-index: 1000;"></ul>
        </div>
        """
        
        # Wrap input and suggestions in positioned container
        return mark_safe(f"<div class='keyword-input-wrapper position-relative'>{input_html}{suggestions_html}</div>")