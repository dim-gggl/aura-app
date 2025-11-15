"""
Django admin configuration for the artworks application.

This module configures the Django admin interface for all artwork-related models,
providing comprehensive management capabilities for administrators. The admin
interface includes advanced features like inline editing, filtering, searching,
and organized fieldsets for better usability.

Key features:
- Artwork management with inline photo editing
- Advanced filtering and search capabilities
- Organized fieldsets for complex forms
- Readonly fields for system-generated data
- Horizontal filter widgets for many-to-many relationships
"""

from django.contrib import admin

from .models import (Artist, Artwork, ArtworkAttachment, ArtworkPhoto,
                     Collection, Exhibition, WishlistItem)


class ArtworkPhotoInline(admin.TabularInline):
    """
    Inline admin for managing artwork photos within the artwork admin.

    Allows administrators to add, edit, and delete photos directly
    from the artwork editing page. Uses tabular layout for compact display.
    """

    model = ArtworkPhoto
    extra = 1  # Show one empty form by default
    fields = ["image", "caption", "is_primary"]
    readonly_fields = ["created_at"]


class ArtworkAttachmentInline(admin.TabularInline):
    """Inline admin for managing artwork attachments."""

    model = ArtworkAttachment
    extra = 1
    fields = ["file", "title", "notes", "uploaded_at"]
    readonly_fields = ["uploaded_at"]


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    """
    Admin configuration for Artist model.

    Provides comprehensive artist management with search, filtering,
    and organized display of biographical information.
    """

    list_display = ["name", "nationality", "birth_year", "death_year"]
    list_filter = ["nationality", "birth_year"]
    search_fields = ["name", "nationality", "biography"]
    ordering = ["name"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "nationality")}),
        (
            "Life Dates",
            {
                "fields": ("birth_year", "death_year"),
                "description": "Enter years as numbers (e.g., 1850, 1920)",
            },
        ),
        ("Biography", {"fields": ("biography",), "classes": ("wide",)}),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
                "description": "System-generated timestamps",
            },
        ),
    )
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    """
    Admin configuration for Artwork model.

    The most complex admin configuration with comprehensive filtering,
    searching, and organized fieldsets. Includes inline photo management
    and horizontal filter widgets for many-to-many relationships.
    """

    list_display = [
        "title",
        "get_artists_display",
        "art_type",
        "creation_year",
        "current_location",
        "user",
        "is_acquired",
    ]
    list_filter = [
        "art_type",
        "support",
        "technique",
        "current_location",
        "is_signed",
        "is_framed",
        "is_acquired",
        "user",
        "created_at",
    ]
    search_fields = [
        "title",
        "artists__name",
        "notes",
        "contextual_references",
        "provenance",
        "origin_country",
        "acquisition_place",
    ]
    # Horizontal filter widgets for better UX with many-to-many fields
    filter_horizontal = ["artists", "collections", "exhibitions"]
    inlines = [ArtworkPhotoInline, ArtworkAttachmentInline]
    readonly_fields = ["id", "created_at", "updated_at"]

    # Organized fieldsets for better form organization
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "user",
                    "title",
                    "artists",
                    "creation_year",
                    "origin_country",
                ),
                "description": "Essential artwork identification and attribution",
            },
        ),
        (
            "Artistic Characteristics",
            {
                "fields": (
                    "art_type",
                    "support",
                    "technique",
                    "height",
                    "width",
                    "depth",
                    "weight",
                ),
                "description": "Physical and technical characteristics",
            },
        ),
        (
            "Status and Location",
            {
                "fields": (
                    "current_location",
                    "is_signed",
                    "is_framed",
                    "is_borrowed",
                    "is_acquired",
                    "owners",
                ),
                "description": "Current status and ownership information",
            },
        ),
        (
            "Acquisition Details",
            {
                "fields": (
                    "acquisition_date",
                    "acquisition_place",
                    "price",
                    "provenance",
                ),
                "description": "Purchase and provenance information",
            },
        ),
        (
            "Organization",
            {
                "fields": (
                    "collections",
                    "exhibitions",
                    "parent_artwork",
                    "last_exhibited",
                ),
                "description": "Grouping and exhibition history",
            },
        ),
        (
            "Additional Information",
            {
                "fields": ("tags", "contextual_references", "notes"),
                "description": "Supplementary documentation and notes",
            },
        ),
        (
            "System Metadata",
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
                "description": "System-generated fields (read-only)",
            },
        ),
    )

    # Custom queryset optimization
    def get_queryset(self, request):
        """Optimize queryset with select_related for better performance."""
        return (
            super()
            .get_queryset(request)
            .select_related("user", "art_type", "support", "technique")
            .prefetch_related("artists", "collections", "exhibitions")
        )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Collection model.

    Simple admin for managing user collections with basic
    filtering and search capabilities.
    """

    list_display = ["name", "user", "created_at"]
    list_filter = ["user", "created_at"]
    search_fields = ["name", "description"]
    ordering = ["name", "created_at"]

    fieldsets = (
        ("Collection Details", {"fields": ("user", "name", "description")}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
    readonly_fields = ["created_at"]


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Exhibition model.

    Includes date hierarchy for easy navigation through exhibitions
    by date, plus comprehensive filtering and search.
    """

    list_display = ["name", "location", "start_date", "end_date", "user"]
    list_filter = ["user", "start_date", "end_date"]
    search_fields = ["name", "location", "description"]
    # Adds date navigation at top of list
    date_hierarchy = "start_date"
    # Most recent exhibitions first
    ordering = ["-start_date", "created_at", "end_date"]

    fieldsets = (
        ("Exhibition Details", {"fields": ("user", "name", "location")}),
        (
            "Dates",
            {
                "fields": ("start_date", "end_date"),
                "description": "Leave end date empty for ongoing exhibitions",
            },
        ),
        ("Description", {"fields": ("description",), "classes": ("wide",)}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
    readonly_fields = ["created_at"]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for WishlistItem model.

    Manages user wishlist items with priority-based organization
    and comprehensive search capabilities.
    """

    list_display = [
        "title",
        "artist_name",
        "priority",
        "estimated_price",
        "user",
        "created_at",
    ]
    list_filter = ["priority", "user", "created_at"]
    search_fields = ["title", "artist_name", "notes", "source_url"]
    # High priority first, then newest
    ordering = ["priority", "-created_at"]
    fieldsets = (
        ("Wishlist Item", {"fields": ("user", "title", "artist_name")}),
        ("Details", {"fields": ("estimated_price", "priority", "source_url")}),
        ("Notes", {"fields": ("notes",), "classes": ("wide",)}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
    readonly_fields = ["created_at"]

    # Custom actions
    actions = ["mark_high_priority", "mark_low_priority"]

    def mark_high_priority(self, request, queryset):
        """Mark selected wishlist items as high priority."""
        updated = queryset.update(priority=1)
        self.message_user(request, f"{updated} items marked as high priority.")

    mark_high_priority.short_description = "Mark as high priority"

    def mark_low_priority(self, request, queryset):
        """Mark selected wishlist items as low priority."""
        updated = queryset.update(priority=3)
        self.message_user(request, f"{updated} items marked as low priority.")

    mark_low_priority.short_description = "Mark as low priority"
