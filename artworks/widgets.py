"""
Custom Django widgets for the artworks application.

This module provides enhanced form widgets that add dynamic functionality
to forms, allowing users to create new related entities on-the-fly without
leaving the current form. These widgets integrate with AJAX endpoints to
provide a seamless user experience.

Widgets included:
- SelectOrCreateWidget: Single selection with "add new" functionality
- SelectMultipleOrCreateWidget: Multiple selection with "add new" functionality
 - TagWidget: (legacy) Text input for keywords/tags [no longer used]

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
            create_url_name: URL for the AJAX endpoint (for example
                'artworks:artist_create_ajax')
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
        # Ensure Bootstrap styling for select
        existing_class = attrs.get("class", "")
        if "form-select" not in existing_class:
            existing_class = (existing_class + " form-select").strip()
        attrs["class"] = (existing_class + " select-or-create").strip()
        attrs["data-create-url"] = reverse_lazy(self.create_url_name)

        # Render the standard select element
        select_html = super().render(name, value, attrs, renderer)

        # Add the creation button (icon-only with a tooltip)
        add_button_html = (
            '<button type="button"\n'
            '        class="btn btn-outline-secondary add-new-btn"\n'
            f'        aria-label="Add {self.model_class._meta.verbose_name}"\n'
            '        data-bs-toggle="tooltip"\n'
            '        data-bs-placement="top"\n'
            f'        title="Add {self.model_class._meta.verbose_name.lower()}"\n'
            f'        data-field-name="{name}"\n'
            f'        data-model-name="{self.model_class._meta.verbose_name}">\n'
            '  <i class="bi bi-plus-lg"></i>\n'
            "</button>"
        )

        wrapper_html = (
            "<div class='input-group select-or-create-wrapper'>"
            f"{select_html}{add_button_html}"
            "</div>"
        )
        return mark_safe(wrapper_html)


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
        # Ensure Bootstrap styling for select multiple
        existing_class = attrs.get("class", "")
        if "form-select" not in existing_class:
            existing_class = (existing_class + " form-select").strip()
        attrs["class"] = (existing_class + " select-multiple-or-create").strip()
        attrs["data-create-url"] = reverse_lazy(self.create_url_name)
        attrs["multiple"] = True  # Ensure multiple selection is enabled

        # Render the standard multiple select element
        select_html = super().render(name, value, attrs, renderer)

        # Add the creation button (icon-only with a tooltip)
        add_button_html = (
            '<button type="button"\n'
            '        class="btn btn-outline-secondary add-new-multiple-btn"\n'
            f'        aria-label="Add {self.model_class._meta.verbose_name}"\n'
            '        data-bs-toggle="tooltip"\n'
            '        data-bs-placement="top"\n'
            f'        title="Add {self.model_class._meta.verbose_name.lower()}"\n'
            f'        data-field-name="{name}"\n'
            f'        data-model-name="{self.model_class._meta.verbose_name}">\n'
            '  <i class="bi bi-plus-lg"></i>\n'
            "</button>"
        )

        wrapper_html = (
            "<div class='input-group select-multiple-or-create-wrapper'>"
            f"{select_html}{add_button_html}"
            "</div>"
        )

        return mark_safe(wrapper_html)


class TagWidget(forms.TextInput):
    """
    Legacy keyword input kept for backwards compatibility.

    It is not used with django-taggit anymore but remains for migration safety.
    """

    pass
