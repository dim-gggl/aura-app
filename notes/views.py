"""
Views for the notes application.

This module provides comprehensive CRUD operations and management features
for personal notes within the art collection system. It includes advanced
filtering, search functionality, favorites management, and pagination.

Key features:
- Complete CRUD operations for notes
- Text search across title and content
- Favorites filtering and toggle functionality
- Pagination for large note collections
- User-specific data isolation for security
- Comprehensive error handling and user feedback
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .forms import NoteForm
from .models import Note


@login_required
def note_list(request):
    """
    Display a paginated and filterable list of user's notes.

    This view provides comprehensive note management with:
    - Text search across title and content fields
    - Favorites-only filtering for quick access
    - Pagination for performance with large note collections
    - Most recent notes displayed first
    - User-specific data isolation for security

    Search and filter parameters are preserved across pagination to maintain
    user experience during navigation.

    Args:
        request: HTTP request object with optional GET parameters:
                - search: Text search across title and content
                - favorites: Show only favorite notes if present
                - page: Pagination page number

    Returns:
        HttpResponse: Rendered note list with pagination and filters
    """
    # Get all notes for the current user
    notes = Note._default_manager.filter(user=request.user)

    # === FILTERING AND SEARCH ===
    # Extract filter parameters from GET request
    search = request.GET.get("search", "").strip()
    favorites_only = request.GET.get("favorites", "")

    # Apply text search across title and content if provided
    if search:
        notes = notes.filter(
            Q(title__icontains=search)  # Search in note title
            | Q(content__icontains=search)  # Search in note content
        )

    # Apply favorites filter if requested
    if favorites_only:
        notes = notes.filter(is_favorite=True)

    # Order by most recently updated first
    notes = notes.order_by("-updated_at")

    # === PAGINATION ===
    # Implement pagination for better performance and UX
    paginator = Paginator(notes, 15)  # 15 notes per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # === CONTEXT PREPARATION ===
    context = {
        "notes": page_obj,  # Paginated note list
        "current_filters": {
            "search": search,
            "favorites": favorites_only,
        },  # Preserve current filters for form population
        "total_notes": notes.count(),  # Total count for display
        "favorite_count": Note._default_manager.filter(
            user=request.user, is_favorite=True
        ).count(),
    }

    return render(request, "notes/note_list.html", context)


@login_required
def note_create(request):
    """
    Handle creation of new notes.

    Provides a form for creating new notes with title, content, and favorite
    status. On successful creation, redirects to the note list with a
    success message.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Note creation form (GET) or redirect to list (POST success)
    """
    if request.method == "POST":
        # Process form submission
        form = NoteForm(request.POST)
        if form.is_valid():
            # Save note but don't commit to DB yet (need to set user)
            note = form.save(commit=False)
            note.user = request.user  # Associate with current user
            note.save()

            # Provide success feedback and redirect
            messages.success(request, "Note créée avec succès.")
            return redirect("notes:detail", pk=note.pk)  # Redirect to detail view
    else:
        # GET request - display empty form
        form = NoteForm()

    context = {
        "form": form,
        "title": "Nouvelle note",
    }

    return render(request, "notes/note_form.html", context)


@login_required
def note_detail(request, pk):
    """
    Display detailed information about a specific note.

    Shows comprehensive note information including content, metadata,
    and favorite status. Only accessible to the note's owner for security.

    Args:
        request: HTTP request object
        pk: Primary key of the note to display

    Returns:
        HttpResponse: Rendered note detail page

    Raises:
        Http404: If note doesn't exist or doesn't belong to current user
    """
    # Ensure note exists and belongs to current user
    note = get_object_or_404(Note, pk=pk, user=request.user)

    context = {
        "note": note,
        "word_count": note.get_word_count(),
        "is_recent": note.is_recently_updated(),
    }

    return render(request, "notes/note_detail.html", context)


@login_required
def note_export_html(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    html_content = render_to_string(
        "notes/note_export.html",
        {
            "note": note,
        },
    )
    response = HttpResponse(html_content, content_type="text/html")
    response["Content-Disposition"] = f"attachment; filename='note_{note.pk}.html'"
    return response


@login_required
def note_export_pdf(request, pk):
    try:
        from weasyprint import HTML
    except (ImportError, OSError):
        message = (
            "PDF export is not available because the required WeasyPrint "
            "system dependencies are missing."
        )
        messages.error(request, message)
        return redirect("notes:detail", pk=pk)
    note = get_object_or_404(Note, pk=pk, user=request.user)
    html_content = render_to_string(
        "notes/note_export.html",
        {
            "note": note,
            "is_pdf": True,
        },
    )
    pdf = HTML(string=html_content).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename='note_{note.pk}.pdf'"
    return response


@login_required
def note_update(request, pk):
    """
    Handle updating existing notes.

    Provides a pre-populated form for editing note information.
    On successful update, redirects to the note detail page with
    a success message.

    Args:
        request: HTTP request object
        pk: Primary key of the note to update

    Returns:
        HttpResponse: Note edit form (GET) or redirect to detail (POST success)

    Raises:
        Http404: If note doesn't exist or doesn't belong to current user
    """
    # Ensure note exists and belongs to current user
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == "POST":
        # Process form submission with existing note instance
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()  # updated_at is automatically updated

            # Provide success feedback and redirect to detail view
            messages.success(request, "Note modifiée avec succès.")
            return redirect("notes:detail", pk=note.pk)
    else:
        # GET request - display form with current note data
        form = NoteForm(instance=note)

    context = {
        "form": form,
        "note": note,
        "title": "Modifier la note",
    }

    return render(request, "notes/note_form.html", context)


@login_required
def note_delete(request, pk):
    """
    Handle note deletion with confirmation.

    Displays a confirmation page for GET requests and processes the
    deletion for POST requests. This two-step process prevents
    accidental deletions.

    Args:
        request: HTTP request object
        pk: Primary key of the note to delete

    Returns:
        HttpResponse: Confirmation page (GET) or redirect to list (POST)

    Raises:
        Http404: If note doesn't exist or doesn't belong to current user
    """
    # Ensure note exists and belongs to current user
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == "POST":
        # Confirmed deletion - remove note and redirect
        note_title = note.title  # Store title for success message
        note.delete()

        messages.success(request, f'Note "{note_title}" supprimée avec succès.')
        return redirect("notes:list")

    # GET request - show confirmation page
    context = {
        "note": note,
    }

    return render(request, "notes/note_confirm_delete.html", context)


@login_required
def note_toggle_favorite(request, pk):
    """
    Toggle the favorite status of a note.

    This view allows users to quickly mark or unmark notes as favorites
    for easy access from the dashboard and filtered lists. Provides
    immediate feedback about the status change.

    Args:
        request: HTTP request object
        pk: Primary key of the note to toggle

    Returns:
        HttpResponse: Redirect to note detail page with status message

    Raises:
        Http404: If note doesn't exist or doesn't belong to current user
    """
    # Ensure note exists and belongs to current user
    note = get_object_or_404(Note, pk=pk, user=request.user)

    # Toggle favorite status using the model method
    new_status = note.toggle_favorite()

    # Provide appropriate feedback message
    status_text = "ajoutée aux" if new_status else "retirée des"
    messages.success(request, f"Note {status_text} favoris.")

    # Redirect back to note detail page
    return redirect("notes:detail", pk=note.pk)


@require_POST
@login_required
def note_toggle_favorite_ajax(request, pk):
    """
    AJAX endpoint for toggling note favorite status.

    This view provides an AJAX alternative to the regular favorite toggle
    for dynamic UI updates without page reloads. Returns JSON response
    with the new status for frontend JavaScript handling.

    Args:
        request: HTTP request object (must be POST)
        pk: Primary key of the note to toggle

    Returns:
        JsonResponse: JSON with success status and new favorite state

    Raises:
        Http404: If note doesn't exist or doesn't belong to current user
    """
    try:
        # Ensure note exists and belongs to current user
        note = get_object_or_404(Note, pk=pk, user=request.user)

        # Toggle favorite status
        new_status = note.toggle_favorite()

        return JsonResponse(
            {
                "success": True,
                "is_favorite": new_status,
                "message": (
                    "Note added to favorites."
                    if new_status
                    else "Note removed from favorites."
                ),
            }
        )

    except Exception as e:
        # Log the full error for debugging (server-side only)
        logging.error(f"Error toggling note favorite status: {str(e)}", exc_info=True)

        error_message = "An error occurred while updating the favorite flag."
        return JsonResponse({"error": error_message}, status=500)
