"""
Django models for the contacts application.

This module defines the Contact model for managing professional contacts
in the art world. Contacts represent galleries, museums, collectors, experts,
and other professionals that users interact with in their art collection
management activities.

The Contact model provides comprehensive contact information storage with
categorization by contact type for better organization and filtering.
"""

from django.db import models
from django.urls import reverse

from core.models import User


class Contact(models.Model):
    """
    Model representing a professional contact in the art world.

    Contacts are user-specific entities that store information about galleries,
    museums, collectors, experts, and other professionals. This model provides
    comprehensive contact information management with categorization and
    relationship tracking.

    Key features:
    - Categorization by contact type for organization
    - Complete contact information (address, phone, email, website)
    - User-specific data isolation
    - Notes field for additional information
    - Timestamps for tracking creation and updates

    Use cases:
    - Gallery and dealer management
    - Museum and institution contacts
    - Expert and appraiser information
    - Service provider tracking (restoration, transport, insurance)
    - Collector network management
    """

    # Contact type categories for art world professionals
    CONTACT_TYPES = [
        ("galerie", "Galerie"),  # Art galleries and dealers
        ("musee", "Musée"),  # Museums and institutions
        ("collectionneur", "Collectionneur"),  # Private collectors
        ("expert", "Expert"),  # Appraisers and authenticators
        ("restaurateur", "Restaurateur"),  # Art restorers and conservators
        ("transporteur", "Transporteur"),  # Art transport and logistics
        ("assureur", "Assureur"),  # Insurance providers
        ("autre", "Autre"),  # Other types of contacts
    ]

    # === CORE FIELDS ===
    # User relationship for data isolation
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contacts",
        help_text="Owner of this contact",
    )

    # Basic identification
    name = models.CharField(
        max_length=200,
        verbose_name="Nom",
        help_text="Name of the person or organization",
    )

    # Contact categorization
    contact_type = models.CharField(
        max_length=50,
        choices=CONTACT_TYPES,
        verbose_name="Type",
        help_text="Type of professional contact",
    )

    # === CONTACT INFORMATION ===
    # Physical address (can be multi-line)
    address = models.TextField(
        blank=True, verbose_name="Adresse", help_text="Complete mailing address"
    )

    # Phone number (flexible format)
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone",
        help_text="Primary phone number",
    )

    # Email address with validation
    email = models.EmailField(
        blank=True, verbose_name="Email", help_text="Primary email address"
    )

    # Website URL with validation
    website = models.URLField(
        blank=True, verbose_name="Site web", help_text="Website or social media URL"
    )

    # === ADDITIONAL INFORMATION ===
    # Free-form notes for additional details
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Additional notes, specialties, or relationship details",
    )

    # === METADATA ===
    # Automatic timestamps
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this contact was added"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this contact was last updated"
    )

    class Meta:
        ordering = ["name"]  # Alphabetical ordering by name
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

        # Ensure unique contact names per user (optional constraint)
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['user', 'name'],
        #         name='unique_contact_per_user'
        #     )
        # ]

    def __str__(self):
        """
        Return string representation of the contact.

        Returns:
            str: Contact name
        """
        return self.name

    def get_absolute_url(self):
        """
        Return the canonical URL for this contact's detail view.

        Returns:
            str: URL path to contact detail page
        """
        return reverse("contacts:detail", kwargs={"pk": self.pk})

    def get_contact_type_display_verbose(self):
        """
        Get a more descriptive display of the contact type.

        Returns:
            str: Human-readable contact type with additional context
        """
        type_descriptions = {
            "galerie": "Galerie d'art / Marchand",
            "musee": "Musée / Institution culturelle",
            "collectionneur": "Collectionneur privé",
            "expert": "Expert / Commissaire-priseur",
            "restaurateur": "Restaurateur / Conservateur",
            "transporteur": "Transporteur spécialisé",
            "assureur": "Assureur / Courtier",
            "autre": "Autre professionnel",
        }
        return type_descriptions.get(self.contact_type, self.get_contact_type_display())

    def has_complete_contact_info(self):
        """
        Check if the contact has complete contact information.

        Returns:
            bool: True if contact has at least phone or email
        """
        return bool(self.phone or self.email)

    def get_primary_contact_method(self):
        """
        Get the primary contact method for this contact.

        Returns:
            str: Primary contact method ('email', 'phone', or 'address')
        """
        if self.email:
            return "email"
        elif self.phone:
            return "phone"
        elif self.address:
            return "address"
        else:
            return "none"

    @classmethod
    def get_contacts_by_type(cls, user, contact_type):
        """
        Get all contacts of a specific type for a user.

        Args:
            user: User instance
            contact_type: Contact type to filter by

        Returns:
            QuerySet: Contacts of the specified type
        """
        return cls.objects.filter(user=user, contact_type=contact_type)
