"""
Views for the artworks application.

This module contains all the view functions for managing artworks, artists,
collections, exhibitions, and related entities. It provides both regular
views for the web interface and AJAX endpoints for dynamic functionality.

The views are organized into the following sections:
- Artwork CRUD operations
- Artist management
- Collection management
- Exhibition management
- Wishlist functionality
- Reference entity management (ArtType, Support, Technique, Keyword)
- AJAX endpoints for dynamic form interactions
- Export functionality
"""

import json
import logging
import random  # Used for random artwork suggestions
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from taggit.models import Tag

from .filters import ArtworkFilter

# Import forms for handling user input
from .forms import (
    ArtistForm,
    ArtworkAttachmentFormSet,
    ArtworkForm,
    ArtworkPhotoFormSet,
    CollectionForm,
    ExhibitionForm,
    WishlistItemForm,
)

# Import all models used in the views
from .models import (
    Artist,
    ArtType,
    Artwork,
    Collection,
    Exhibition,
    Support,
    Technique,
    WishlistItem,
)

# ========================================
# UTILITAIRES COMMUNS
# ========================================


def _export_response_from_template(
    *,
    request,
    template_name: str,
    context: dict,
    filename_base: str,
    as_pdf: bool = False,
    redirect_response=None,
):
    """
    Génère une réponse d'export (HTML ou PDF) à partir d'un template.

    - Ajoute automatiquement `is_pdf` au contexte pour les templates.
    - Gère l'import de WeasyPrint et le message d'erreur utilisateur.
    """
    if as_pdf:
        try:
            from weasyprint import HTML  # type: ignore
        except (ImportError, OSError):
            messages.error(
                request,
                (
                    "L'export PDF n'est pas disponible. Les dépendances "
                    "système de WeasyPrint ne sont pas installées."
                ),
            )
            if redirect_response is not None:
                return redirect_response
            return redirect("artworks:list")

        context = {**context, "is_pdf": True}
        html_content = render_to_string(template_name, context)
        pdf = HTML(string=html_content).write_pdf()
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename='{filename_base}.pdf'"
        return response

    # Export HTML
    html_content = render_to_string(template_name, context)
    response = HttpResponse(html_content, content_type="text/html")
    response["Content-Disposition"] = f"attachment; filename='{filename_base}.html'"
    return response


def _reference_list(
    request,
    *,
    model,
    entity_name: str,
    entity_name_plural: str,
    create_url: str,
):
    """Generic list view for reference entities with artwork counters."""
    items = (
        model._default_manager.all().annotate(artwork_count=Count("artwork")).order_by("name")
    )

    search = request.GET.get("search", "")
    if search:
        items = items.filter(name__icontains=search)

    paginator = Paginator(items, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
        "entity_name": entity_name,
        "entity_name_plural": entity_name_plural,
        "create_url": create_url,
    }

    return render(request, "artworks/reference_list.html", context)


def _reference_create(
    request,
    *,
    model,
    entity_label: str,
    back_url_name: str,
    title: str,
):
    """Vue générique de création pour entités Nom uniquement."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            obj, created = model._default_manager.get_or_create(name=name)
            if created:
                messages.success(
                    request, f"{entity_label.capitalize()} '{name}' créé avec succès."
                )
            else:
                messages.info(
                    request, f"{entity_label.capitalize()} '{name}' existe déjà."
                )
            return redirect(back_url_name)
        else:
            messages.error(request, "Le nom est requis.")

    context = {
        "title": title,
        "entity_name": entity_label,
        "back_url": back_url_name,
    }
    return render(request, "artworks/reference_form.html", context)


def _reference_update(
    request,
    pk,
    *,
    model,
    entity_label: str,
    back_url_name: str,
    title: str,
):
    """Vue générique de modification pour entités Nom uniquement."""
    obj = get_object_or_404(model, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            if name != obj.name:
                if model._default_manager.filter(name=name).exists():
                    messages.error(
                        request,
                        f"Un {entity_label} avec le nom '{name}' existe déjà.",
                    )
                else:
                    obj.name = name
                    obj.save()
                    messages.success(
                        request, f"{entity_label.capitalize()} modifié avec succès."
                    )
                    return redirect(back_url_name)
            else:
                return redirect(back_url_name)
        else:
            messages.error(request, "Le nom est requis.")

    context = {
        "title": title,
        "entity_name": entity_label,
        "current_name": obj.name,
        "back_url": back_url_name,
    }
    return render(request, "artworks/reference_form.html", context)


def _reference_delete(
    request,
    pk,
    *,
    model,
    entity_label: str,
    back_url_name: str,
):
    """Vue générique de suppression pour entités Nom uniquement."""
    obj = get_object_or_404(model, pk=pk)

    if request.method == "POST":
        name = obj.name
        obj.delete()
        messages.success(
            request, f"{entity_label.capitalize()} '{name}' supprimé avec succès."
        )
        return redirect(back_url_name)

    context = {
        "object": obj,
        "entity_name": entity_label,
        "back_url": back_url_name,
    }
    return render(request, "artworks/reference_confirm_delete.html", context)


def _create_by_name_ajax_impl(
    request, *, model, with_user: bool = False, defaults: dict | None = None
):
    """Logique générique de création via AJAX d'une entité identifiée par son nom."""
    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        if not name:
            return JsonResponse({"error": "Le nom est requis"}, status=400)

        kwargs = {"name": name}
        if with_user:
            kwargs["user"] = request.user

        obj, created = model._default_manager.get_or_create(defaults=defaults or {}, **kwargs)
        return JsonResponse(
            {
                "success": True,
                "id": obj.pk,
                "name": getattr(obj, "name", str(obj.pk)),
                "created": created,
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        # Log the full error for debugging (server-side only)
        logging.error(f"Error in AJAX entity creation: {str(e)}", exc_info=True)

        return JsonResponse(
            {"error": "Une erreur est survenue lors de la création."}, status=500
        )


# ========================================
# ARTWORK VIEWS
# ========================================

# LIST ================================


@login_required
def artwork_list(request):
    """
    Display a paginated and filterable list of the user's artworks.

    This view provides the main artwork listing page with:
    - Filtering by various criteria (artist, type, location, etc.)
    - Search functionality
    - Pagination (12 items per page)
    - Optimized queries with prefetch_related for performance

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered artwork list page
    """
    # Get all user's artworks with optimized queries to reduce database hits
    # prefetch_related loads related artists and photos in separate queries
    artworks = Artwork._default_manager.filter(user=request.user).prefetch_related(
        "artists", "photos"
    )

    # Get artists that have artworks for this user (for filter dropdown)
    artist_queryset = Artist._default_manager.filter(artwork__user=request.user).distinct()

    # Apply filters based on GET parameters
    artwork_filter = ArtworkFilter(request.GET, queryset=artworks)
    # Limit filter dropdowns to current user's data
    artwork_fields = artwork_filter.form.fields
    artwork_fields["artists"].queryset = artist_queryset
    if "collections" in artwork_fields:
        artwork_fields["collections"].queryset = Collection._default_manager.filter(
            user=request.user
        )

    if "exhibitions" in artwork_fields:
        artwork_fields["exhibitions"].queryset = Exhibition._default_manager.filter(
            user=request.user
        )

    if "parent_artwork" in artwork_fields:
        artwork_fields["parent_artwork"].queryset = Artwork._default_manager.filter(
            user=request.user
        )

    if "tags" in artwork_fields:
        artwork_ct = ContentType._default_manager.get_for_model(Artwork)
        user_artwork_ids = Artwork._default_manager.filter(user=request.user).values_list(
            "id", flat=True
        )
        artwork_fields["tags"].queryset = (
            Tag._default_manager.filter(
                artworks_artworks_uuidtaggeditem_items__content_type=artwork_ct,
                artworks_artworks_uuidtaggeditem_items__object_id__in=user_artwork_ids,
            )
            .distinct()
            .order_by("name")
        )

    # Use filtered queryset for pagination
    artworks = artwork_filter.qs.prefetch_related("artists", "photos")
    paginator = Paginator(artworks, 12)  # 12 artworks per page for grid layout
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Build helpers for templates: active filters and querystring without page
    # Keep multi-valued params intact for pagination links
    get_params = request.GET.copy()
    if "page" in get_params:
        del get_params["page"]

    current_filters = {k: ", ".join(get_params.getlist(k)) for k in get_params}
    querystring = get_params.urlencode()

    context = {
        "filter": artwork_filter,
        "page_obj": page_obj,
        "current_filters": current_filters,
        "querystring": querystring,
    }

    return render(request, "artworks/artwork_list.html", context)


# DETAIL ================================


@login_required
def artwork_detail(request, pk):
    """
    Display detailed information about a specific artwork.

    Shows comprehensive artwork information including photos, dimensions,
    acquisition details, and related entities. Only accessible to the
    artwork's owner for security.

    Args:
        request: The HTTP request object
        pk: Primary key (UUID) of the artwork to display

    Returns:
        HttpResponse: Rendered artwork detail page

    Raises:
        Http404: If artwork doesn't exist or doesn't belong to current user
    """
    # get_object_or_404 ensures artwork exists and belongs to current user
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
    # Get all photos for this artwork, ordered by primary status
    photos = artwork.photos.all()

    context = {
        "artwork": artwork,
        "photos": photos,
    }

    return render(request, "artworks/artwork_detail.html", context)


# CREATE ================================


@login_required
def artwork_create(request):
    """
    Handle creation of new artworks with photos.

    This view manages both the artwork form and associated photo formset.
    On successful creation, the user is redirected to the artwork detail page.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered form page (GET) or redirect to detail page
        (POST success)
    """
    if request.method == "POST":
        # Initialize forms with POST data and files
        form = ArtworkForm(request.POST, request.FILES, user=request.user)
        photo_formset = ArtworkPhotoFormSet(
            request.POST, request.FILES, prefix="photos"
        )
        attachment_formset = ArtworkAttachmentFormSet(
            request.POST, request.FILES, prefix="attachments"
        )

        if (
            form.is_valid()
            and photo_formset.is_valid()
            and attachment_formset.is_valid()
        ):
            # Save artwork but don't commit to DB yet (need to set user)
            artwork = form.save(commit=False)
            artwork.user = request.user
            artwork.save()
            # Save many-to-many relationships after the main object is saved
            form.save_m2m()

            # Associate photo formset with the saved artwork and save photos
            photo_formset.instance = artwork
            photo_formset.save()

            # Associate attachment formset and save attachments
            attachment_formset.instance = artwork
            attachment_formset.save()

            messages.success(request, "Oeuvre ajoutée avec succès.")
            return redirect("artworks:detail", pk=artwork.pk)
    else:
        # GET request: initialize empty forms
        form = ArtworkForm(user=request.user)
        photo_formset = ArtworkPhotoFormSet(prefix="photos")
        attachment_formset = ArtworkAttachmentFormSet(prefix="attachments")

    context = {
        "form": form,
        "photo_formset": photo_formset,
        "attachment_formset": attachment_formset,
        "title": "Ajouter une œuvre",
    }

    return render(request, "artworks/artwork_form.html", context)


# UPDATE ================================


@login_required
def artwork_update(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)

    if request.method == "POST":
        form = ArtworkForm(
            request.POST, request.FILES, instance=artwork, user=request.user
        )
        photo_formset = ArtworkPhotoFormSet(
            request.POST, request.FILES, instance=artwork, prefix="photos"
        )
        attachment_formset = ArtworkAttachmentFormSet(
            request.POST, request.FILES, instance=artwork, prefix="attachments"
        )

        if (
            form.is_valid()
            and photo_formset.is_valid()
            and attachment_formset.is_valid()
        ):
            form.save()
            photo_formset.save()
            attachment_formset.save()

            messages.success(request, "Œuvre modifiée avec succès.")
            return redirect("artworks:detail", pk=artwork.pk)
    else:
        form = ArtworkForm(instance=artwork, user=request.user)
        photo_formset = ArtworkPhotoFormSet(instance=artwork, prefix="photos")
        attachment_formset = ArtworkAttachmentFormSet(
            instance=artwork, prefix="attachments"
        )

    context = {
        "form": form,
        "photo_formset": photo_formset,
        "attachment_formset": attachment_formset,
        "artwork": artwork,
        "title": 'Modifier l"œuvre',
    }

    return render(request, "artworks/artwork_form.html", context)


# DELETE ================================


@login_required
def artwork_delete(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)

    if request.method == "POST":
        artwork.delete()
        messages.success(request, "Œuvre supprimée avec succès.")
        return redirect("artworks:list")

    return render(request, "artworks/artwork_confirm_delete.html", {"artwork": artwork})


# EXPORT ================================


@login_required
def artwork_export_html(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
    return _export_response_from_template(
        request=request,
        template_name="artworks/artwork_export.html",
        context={
            "artwork": artwork,
            "photos": artwork.photos.all(),
        },
        filename_base=f"artwork_{artwork.pk}",
        as_pdf=False,
    )


@login_required
def artwork_export_pdf(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
    return _export_response_from_template(
        request=request,
        template_name="artworks/artwork_export.html",
        context={
            "artwork": artwork,
            "photos": artwork.photos.all(),
        },
        filename_base=f"artwork_{artwork.pk}",
        as_pdf=True,
        redirect_response=redirect("artworks:detail", pk=pk),
    )


# ========================================
# RANDOM SUGGESTION FEATURE
# ========================================


@login_required
def random_suggestion(request):
    """
    Suggest a random artwork for exhibition from user's collection.

    This feature helps users discover artworks in their collection that haven't
    been exhibited recently (more than 6 months ago) or never exhibited.
    Only considers artworks currently at home or in storage.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Page with suggested artwork or "no suggestion" message
    """
    try:
        # Define "recently exhibited" as within the last 6 months
        six_months_ago = datetime.now().date() - timedelta(days=180)

        # Find artworks that are available for exhibition:
        # - Located at home or in storage (not already on display/loan)
        # - Not exhibited recently or never exhibited
        artworks = Artwork._default_manager.filter(
            user=request.user,
            current_location__in=["domicile", "stockage"],  # Available locations
        ).filter(
            # Either last exhibited more than 6 months ago OR never exhibited
            Q(last_exhibited__lt=six_months_ago)
            | Q(last_exhibited__isnull=True)
        )

        if artworks.exists():
            # Convert queryset to list to avoid issues with random.choice on querysets
            # This loads all matching artworks into memory but improves reliability
            artworks_list = list(artworks)
            suggested_artwork = random.choice(artworks_list)
            return render(
                request,
                "artworks/random_suggestion.html",
                {"artwork": suggested_artwork},
            )
        else:
            # No artworks available for suggestion
            return render(
                request, "artworks/random_suggestion.html", {"no_suggestion": True}
            )
    except Exception as e:
        # Log the full error for debugging (server-side only)
        logging.error(
            f"Error generating random artwork suggestion: {str(e)}", exc_info=True
        )

        # Graceful error handling - redirect with user-friendly message
        messages.error(
            request, "Une erreur est survenue lors de la génération de la suggestion."
        )
        return redirect("artworks:list")


# ========================================
# ARTIST MANAGEMENT VIEWS
# ========================================

# LIST ================================


@login_required
def artist_list(request):
    """
    Display every artist with a per-user artwork counter.

    - Lists all artists even when they have zero artworks
    - Annotates `artwork_count` with the number of artworks owned by the user
    - Allows searching by name
    """
    # Afficher uniquement les artistes de l'utilisateur et annoter le nombre d'œuvres
    artists = (
        Artist._default_manager.filter(user=request.user)
        .annotate(artwork_count=Count("artwork", filter=Q(artwork__user=request.user)))
        .order_by("name")
    )

    # Handle search functionality
    search = request.GET.get("search", "")
    if search:
        # Case-insensitive search in artist names
        artists = artists.filter(name__icontains=search)

    # Pagination with more items per page since artist list is simpler
    paginator = Paginator(artists, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
    }

    return render(request, "artworks/artist_list.html", context)


# DETAIL ================================


@login_required
def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk, user=request.user)
    artworks = Artwork._default_manager.filter(artists=artist, user=request.user)

    context = {
        "artist": artist,
        "artworks": artworks,
    }

    return render(request, "artworks/artist_detail.html", context)


# CREATE ================================


@login_required
def artist_create(request):
    if request.method == "POST":
        form = ArtistForm(request.POST)
        if form.is_valid():
            artist = form.save(commit=False)
            artist.user = request.user
            artist.save()
            messages.success(request, "Artiste ajouté avec succès.")
            return redirect("artworks:artist_detail", pk=artist.pk)
    else:
        form = ArtistForm()

    context = {
        "form": form,
        "title": "Ajouter un artiste",
    }

    return render(request, "artworks/artist_form.html", context)


# UPDATE ================================


@login_required
def artist_update(request, pk):
    artist = get_object_or_404(Artist, pk=pk, user=request.user)

    if request.method == "POST":
        form = ArtistForm(request.POST, instance=artist)
        if form.is_valid():
            form.save()
            messages.success(request, "Artiste modifié avec succès.")
            return redirect("artworks:artist_detail", pk=artist.pk)
    else:
        form = ArtistForm(instance=artist)

    context = {
        "form": form,
        "artist": artist,
        "title": 'Modifier l"artiste',
    }

    return render(request, "artworks/artist_form.html", context)


# DELETE ================================


@login_required
def artist_delete(request, pk):
    """
    Supprimer un artiste après confirmation.
    Si l'artiste est lié à des œuvres, ces liens seront supprimés (M2M),
    les œuvres ne sont pas supprimées.
    """
    artist = get_object_or_404(Artist, pk=pk)
    # Count the user's current artworks linked to this artist (for information)
    linked_artworks_count = Artwork._default_manager.filter(
        artists=artist, user=request.user
    ).count()
    # If the artist is linked to artworks, these links will be removed (M2M),
    # but the artworks themselves will not be deleted.
    if request.method == "POST":
        name = artist.name
        artist.delete()
        messages.success(request, f"Artiste '{name}' supprimé avec succès.")
        return redirect("artworks:artist_list")

    context = {
        "artist": artist,
        "linked_artworks_count": linked_artworks_count,
    }
    return render(request, "artworks/artist_confirm_delete.html", context)


# EXPORT ================================


@login_required
def artist_export_html(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    artworks = Artwork._default_manager.filter(artists=artist, user=request.user)
    return _export_response_from_template(
        request=request,
        template_name="artworks/artist_export.html",
        context={"artist": artist, "artworks": artworks},
        filename_base=f"artist_{artist.pk}",
        as_pdf=False,
    )


@login_required
def artist_export_pdf(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    artworks = Artwork._default_manager.filter(artists=artist, user=request.user)
    return _export_response_from_template(
        request=request,
        template_name="artworks/artist_export.html",
        context={"artist": artist, "artworks": artworks},
        filename_base=f"artist_{artist.pk}",
        as_pdf=True,
        redirect_response=redirect("artworks:artist_detail", pk=pk),
    )


# ========================================
# COLLECTION MANAGEMENT VIEWS
# ========================================

# LIST ================================


@login_required
def collection_list(request):
    collections = (
        Collection._default_manager.filter(user=request.user)
        .annotate(artwork_count=Count("artwork"))
        .order_by("name")
    )

    search = request.GET.get("search", "")
    if search:
        collections = collections.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    paginator = Paginator(collections, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
    }

    return render(request, "artworks/collection_list.html", context)


# DETAIL ================================


@login_required
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    artworks = collection.artwork_set.all()

    context = {
        "collection": collection,
        "artworks": artworks,
    }

    return render(request, "artworks/collection_detail.html", context)


# CREATE ================================


@login_required
def collection_create(request):
    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.user = request.user
            collection.save()
            messages.success(request, "Collection créée avec succès.")
            return redirect("artworks:collection_detail", pk=collection.pk)
    else:
        form = CollectionForm()

    context = {
        "form": form,
        "title": "Créer une collection",
    }

    return render(request, "artworks/collection_form.html", context)


# UPDATE ================================


@login_required
def collection_update(request, pk):
    collection = get_object_or_404(Collection, pk=pk, user=request.user)

    if request.method == "POST":
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, "Collection modifiée avec succès.")
            return redirect("artworks:collection_detail", pk=collection.pk)
    else:
        form = CollectionForm(instance=collection)

    context = {
        "form": form,
        "collection": collection,
        "title": "Modifier la collection",
    }

    return render(request, "artworks/collection_form.html", context)


# DELETE ================================


@login_required
def collection_delete(request, pk):
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    if request.method == "POST":
        collection.delete()
        messages.success(request, "Collection supprimée avec succès.")
        return redirect("artworks:collection_list")
    return render(
        request, "artworks/collection_confirm_delete.html", {"collection": collection}
    )


# EXPORT ================================


@login_required
def collection_export_html(request, pk):
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    artworks = collection.artwork_set.all()
    return _export_response_from_template(
        request=request,
        template_name="artworks/collection_export.html",
        context={"collection": collection, "artworks": artworks},
        filename_base=f"collection_{collection.pk}",
        as_pdf=False,
    )


@login_required
def collection_export_pdf(request, pk):
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    artworks = collection.artwork_set.all()
    return _export_response_from_template(
        request=request,
        template_name="artworks/collection_export.html",
        context={"collection": collection, "artworks": artworks},
        filename_base=f"collection_{collection.pk}",
        as_pdf=True,
        redirect_response=redirect("artworks:collection_detail", pk=pk),
    )


# ========================================
# EXHIBITION MANAGEMENT VIEWS
# ========================================

# LIST ================================


@login_required
def exhibition_list(request):
    exhibitions = (
        Exhibition._default_manager.filter(user=request.user)
        .annotate(artwork_count=Count("artwork"))
        .order_by("-start_date")
    )

    search = request.GET.get("search", "")
    if search:
        exhibitions = exhibitions.filter(
            Q(name__icontains=search)
            | Q(location__icontains=search)
            | Q(description__icontains=search)
        )

    paginator = Paginator(exhibitions, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
    }

    return render(request, "artworks/exhibition_list.html", context)


# DETAIL ================================


@login_required
def exhibition_detail(request, pk):
    exhibition = get_object_or_404(Exhibition, pk=pk, user=request.user)
    artworks = exhibition.artwork_set.all()

    context = {
        "exhibition": exhibition,
        "artworks": artworks,
    }

    return render(request, "artworks/exhibition_detail.html", context)


# CREATE ================================


@login_required
def exhibition_create(request):
    if request.method == "POST":
        form = ExhibitionForm(request.POST)
        if form.is_valid():
            exhibition = form.save(commit=False)
            exhibition.user = request.user
            exhibition.save()
            messages.success(request, "Exposition créée avec succès.")
            return redirect("artworks:exhibition_detail", pk=exhibition.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
            # Optionnel: afficher les erreurs détaillées en développement
            # messages.error(request, form.errors.as_ul())
    else:
        form = ExhibitionForm()

    context = {
        "form": form,
        "title": "Créer une exposition",
        "cancel_url": "artworks:exhibition_list",
    }

    return render(request, "artworks/exhibition_form.html", context)


# UPDATE ================================


@login_required
def exhibition_update(request, pk):
    exhibition = get_object_or_404(Exhibition, pk=pk, user=request.user)

    if request.method == "POST":
        form = ExhibitionForm(request.POST, instance=exhibition)
        if form.is_valid():
            form.save()
            messages.success(request, "Exposition modifiée avec succès.")
            return redirect("artworks:exhibition_detail", pk=exhibition.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = ExhibitionForm(instance=exhibition)

    context = {
        "form": form,
        "exhibition": exhibition,
        "title": "Modifier l'exposition",
        "cancel_url": "artworks:exhibition_detail",
    }

    return render(request, "artworks/exhibition_form.html", context)


# DELETE ================================


@login_required
def exhibition_delete(request, pk):
    exhibition = get_object_or_404(Exhibition, pk=pk, user=request.user)
    if request.method == "POST":
        exhibition.delete()
        messages.success(request, "Exposition supprimée avec succès.")
        return redirect("artworks:exhibition_list")
    return render(
        request, "artworks/exhibition_confirm_delete.html", {"exhibition": exhibition}
    )


# EXPORT ================================


@login_required
def exhibition_export_html(request, pk):
    exhibition = get_object_or_404(Exhibition, pk=pk, user=request.user)
    artworks = exhibition.artwork_set.all()
    return _export_response_from_template(
        request=request,
        template_name="artworks/exhibition_export.html",
        context={"exhibition": exhibition, "artworks": artworks},
        filename_base=f"exhibition_{exhibition.pk}",
        as_pdf=False,
    )


@login_required
def exhibition_export_pdf(request, pk):
    exhibition = get_object_or_404(Exhibition, pk=pk, user=request.user)
    artworks = exhibition.artwork_set.all()
    return _export_response_from_template(
        request=request,
        template_name="artworks/exhibition_export.html",
        context={"exhibition": exhibition, "artworks": artworks},
        filename_base=f"exhibition_{exhibition.pk}",
        as_pdf=True,
        redirect_response=redirect("artworks:exhibition_detail", pk=pk),
    )


# ========================================
# ART TYPE MANAGEMENT VIEWS
# ========================================

# LIST ================================


@login_required
def arttype_list(request):
    return _reference_list(
        request,
        model=ArtType,
        entity_name="Type d'art",
        entity_name_plural="Types d'art",
        create_url="artworks:arttype_create",
    )


# CREATE ================================


@login_required
def arttype_create(request):
    return _reference_create(
        request,
        model=ArtType,
        entity_label="type d'art",
        back_url_name="artworks:arttype_list",
        title="Ajouter un type d'art",
    )


# UPDATE ================================


@login_required
def arttype_update(request, pk):
    return _reference_update(
        request,
        pk,
        model=ArtType,
        entity_label="type d'art",
        back_url_name="artworks:arttype_list",
        title="Modifier le type d'art",
    )


# DELETE ================================


@login_required
def arttype_delete(request, pk):
    return _reference_delete(
        request,
        pk,
        model=ArtType,
        entity_label="type d'art",
        back_url_name="artworks:arttype_list",
    )


# ========================================
# SUPPORT MANAGEMENT VIEWS
# ========================================

# LIST ================================


@login_required
def support_list(request):
    return _reference_list(
        request,
        model=Support,
        entity_name="Support",
        entity_name_plural="Supports",
        create_url="artworks:support_create",
    )


# CREATE ================================


@login_required
def support_create(request):
    return _reference_create(
        request,
        model=Support,
        entity_label="support",
        back_url_name="artworks:support_list",
        title="Ajouter un support",
    )


# UPDATE ================================


@login_required
def support_update(request, pk):
    return _reference_update(
        request,
        pk,
        model=Support,
        entity_label="support",
        back_url_name="artworks:support_list",
        title="Modifier le support",
    )


# DELETE ================================


@login_required
def support_delete(request, pk):
    return _reference_delete(
        request,
        pk,
        model=Support,
        entity_label="support",
        back_url_name="artworks:support_list",
    )


# ========================================
# TECHNIQUE MANAGEMENT VIEWS
# ========================================

# LIST ================================


@login_required
def technique_list(request):
    return _reference_list(
        request,
        model=Technique,
        entity_name="Technique",
        entity_name_plural="Techniques",
        create_url="artworks:technique_create",
    )


# CREATE ================================


@login_required
def technique_create(request):
    return _reference_create(
        request,
        model=Technique,
        entity_label="technique",
        back_url_name="artworks:technique_list",
        title="Ajouter une technique",
    )


# UPDATE ================================


@login_required
def technique_update(request, pk):
    return _reference_update(
        request,
        pk,
        model=Technique,
        entity_label="technique",
        back_url_name="artworks:technique_list",
        title="Modifier la technique",
    )


# DELETE ================================


@login_required
def technique_delete(request, pk):
    return _reference_delete(
        request,
        pk,
        model=Technique,
        entity_label="technique",
        back_url_name="artworks:technique_list",
    )


# ========================================
# WISHLIST MANAGEMENT VIEWS
# ========================================

# LIST ================================


@login_required
def wishlist(request):
    items = WishlistItem._default_manager.filter(user=request.user)

    if request.method == "POST":
        form = WishlistItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, "Œuvre ajoutée à la liste de souhaits.")
            return redirect("artworks:wishlist")
    else:
        form = WishlistItemForm()

    context = {
        "items": items,
        "form": form,
    }

    return render(request, "artworks/wishlist.html", context)


# DELETE ================================


@login_required
def wishlist_delete(request, pk):
    item = get_object_or_404(WishlistItem, pk=pk, user=request.user)

    if request.method == "POST":
        item.delete()
        messages.success(request, "Œuvre retirée de la liste de souhaits.")
        return redirect("artworks:wishlist")

    return render(request, "artworks/wishlist_confirm_delete.html", {"item": item})


# ========================================
# AJAX ENDPOINTS FOR DYNAMIC FUNCTIONALITY
# ========================================


@require_POST
@login_required
def artist_create_ajax(request):
    """
    Create a new artist via AJAX for dynamic form functionality.

    This endpoint is used by the SelectOrCreateWidget to allow users
    to create new artists on-the-fly while filling out artwork forms.
    Uses get_or_create to prevent duplicates.

    Args:
        request: The HTTP request object with JSON body containing artist name

    Returns:
        JsonResponse: Success response with artist data or error message

    Expected JSON payload:
        {"name": "Artist Name"}

    Response format:
        Success: {"success": True, "id": int, "name": str, "created": bool}
        Error: {"error": str} with appropriate HTTP status code
    """
    # Créer un artiste associé à l'utilisateur courant
    return _create_by_name_ajax_impl(request, model=Artist, with_user=True)


@require_POST
@login_required
def collection_create_ajax(request):
    """Créer une nouvelle collection via AJAX"""
    return _create_by_name_ajax_impl(
        request,
        model=Collection,
        with_user=True,
        defaults={"description": ""},
    )


@require_POST
@login_required
def exhibition_create_ajax(request):
    """Créer une nouvelle exposition via AJAX"""
    return _create_by_name_ajax_impl(
        request,
        model=Exhibition,
        with_user=True,
        defaults={"description": "", "location": ""},
    )


@require_POST
@login_required
def arttype_create_ajax(request):
    """Créer un nouveau type d"art via AJAX"""
    return _create_by_name_ajax_impl(request, model=ArtType)


@require_POST
@login_required
def support_create_ajax(request):
    """Créer un nouveau support via AJAX"""
    return _create_by_name_ajax_impl(request, model=Support)


@require_POST
@login_required
def technique_create_ajax(request):
    """Créer une nouvelle technique via AJAX"""
    return _create_by_name_ajax_impl(request, model=Technique)


# ========================================
# TAGS AUTOCOMPLETE
# ========================================
@login_required
def tags_autocomplete(request):
    """
    Autocompletion of keywords limited to tags used by the current user.
    Format: [{"value": name, "text": name}, ...]
    """
    q = request.GET.get("q", "").strip()
    # Restrict to tags actually used on the user's artworks
    artwork_ct = ContentType._default_manager.get_for_model(Artwork)
    user_artwork_ids = Artwork._default_manager.filter(user=request.user).values_list(
        "id", flat=True
    )

    user_tags = Tag._default_manager.filter(
        artworks_artworks_uuidtaggeditem_items__content_type=artwork_ct,
        artworks_artworks_uuidtaggeditem_items__object_id__in=user_artwork_ids,  # noqa: E501
    ).distinct()
    if q:
        user_tags = user_tags.filter(name__icontains=q)
    user_tags = user_tags.order_by("name")[:20]
    data = [{"value": t.name, "text": t.name} for t in user_tags]
    return JsonResponse(data, safe=False)
