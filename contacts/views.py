"""
Views for the contacts application.

This module provides comprehensive CRUD (Create, Read, Update, Delete) operations
for managing professional contacts in the art world. It includes advanced filtering,
search functionality, and pagination for efficient contact management.

Key features:
- Complete CRUD operations for contacts
- Advanced search across multiple fields
- Filtering by contact type
- Pagination for large contact lists
- User-specific data isolation for security
- Comprehensive error handling and user feedback
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import Contact
from .forms import ContactForm


@login_required
def contact_list(request):
    """
    Display a paginated and filterable list of user's contacts.
    
    This view provides comprehensive contact management with:
    - Search functionality across name, address, email, and notes
    - Filtering by contact type (gallery, museum, collector, etc.)
    - Pagination for performance with large contact lists
    - User-specific data isolation for security
    
    Search and filter parameters are preserved across pagination to maintain
    user experience during navigation.
    
    Args:
        request: HTTP request object with optional GET parameters:
                - search: Text search across multiple fields
                - type: Contact type filter
                - page: Pagination page number
                
    Returns:
        HttpResponse: Rendered contact list with pagination and filters
    """
    # Get all contacts for the current user
    contacts = Contact.objects.filter(user=request.user).only(
        "id", "name", "email", "phone", "contact_type", "created_at"
    )
    
    # === SEARCH FUNCTIONALITY ===
    # Extract search parameters from GET request (robust to missing params)
    search = (request.GET.get('search') or '').strip()
    contact_type = (request.GET.get('type') or '').strip()
    
    # Apply text search across multiple fields if provided
    if search:
        contacts = contacts.filter(
            Q(name__icontains=search) |           # Search in contact name
            Q(address__icontains=search) |        # Search in address
            Q(email__icontains=search) |          # Search in email
            Q(notes__icontains=search)            # Search in notes
        )
    
    # Apply contact type filter if provided
    if contact_type:
        contacts = contacts.filter(contact_type=contact_type)
    
    # Order results alphabetically by name for consistency
    contacts = contacts.order_by('name')
    
    # === PAGINATION ===
    # Implement pagination for better performance and UX
    paginator = Paginator(contacts, 20)  # 20 contacts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # === CONTEXT PREPARATION ===
    context = {
        'contacts': page_obj,  # Paginated contact list
        'contact_types': Contact.CONTACT_TYPES,  # For filter dropdown
        'current_filters': {
            'search': search,
            'type': contact_type,
        },  # Preserve current filters for form population
        'total_contacts': contacts.count(),  # Total count for display
    }
    
    return render(request, 'contacts/contact_list.html', context)


@login_required
def contact_create(request):
    """
    Handle creation of new contacts.
    
    Provides a form for creating new contacts with all required and optional
    fields. On successful creation, redirects to the contact list with a
    success message.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Contact creation form (GET) or redirect to list (POST success)
    """
    if request.method == 'POST':
        # Process form submission
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save contact but don't commit to DB yet (need to set user)
            contact = form.save(commit=False)
            contact.user = request.user  # Associate with current user
            contact.save()
            
            # Provide success feedback and redirect
            messages.success(request, 'Contact ajouté avec succès.')
            return redirect('contacts:list')
    else:
        # GET request - display empty form
        form = ContactForm()
    
    context = {
        'form': form,
        'title': 'Ajouter un contact',
    }
    
    return render(request, 'contacts/contact_form.html', context)


@login_required
def contact_detail(request, pk):
    """
    Display detailed information about a specific contact.
    
    Shows comprehensive contact information including all fields and
    metadata. Only accessible to the contact's owner for security.
    
    Args:
        request: HTTP request object
        pk: Primary key of the contact to display
        
    Returns:
        HttpResponse: Rendered contact detail page
        
    Raises:
        Http404: If contact doesn't exist or doesn't belong to current user
    """
    # Ensure contact exists and belongs to current user
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    
    context = {
        'contact': contact,
    }
    
    return render(request, 'contacts/contact_detail.html', context)


@login_required
def contact_export_html(request, pk):
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    html_content = render_to_string('contacts/contact_export.html', {
        'contact': contact,
        }
    )
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f"attachment; filename='contact_{contact.pk}.html'"
    return response


@login_required
def contact_export_pdf(request, pk):
    try:
        from weasyprint import HTML
    except (ImportError, OSError):
        messages.error(request, "L'export PDF n'est pas disponible. Les dépendances système de WeasyPrint ne sont pas installées.")
        return redirect('contacts:detail', pk=pk)
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    html_content = render_to_string('contacts/contact_export.html', {
        'contact': contact,
        'is_pdf': True,
        }
    )
    pdf = HTML(string=html_content).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f"attachment; filename='contact_{contact.pk}.pdf'"
    return response


@login_required
def contact_update(request, pk):
    """
    Handle updating existing contacts.
    
    Provides a pre-populated form for editing contact information.
    On successful update, redirects to the contact detail page with
    a success message.
    
    Args:
        request: HTTP request object
        pk: Primary key of the contact to update
        
    Returns:
        HttpResponse: Contact edit form (GET) or redirect to detail (POST success)
        
    Raises:
        Http404: If contact doesn't exist or doesn't belong to current user
    """
    # Ensure contact exists and belongs to current user
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Process form submission with existing contact instance
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            
            # Provide success feedback and redirect to detail view
            messages.success(request, 'Contact modifié avec succès.')
            return redirect('contacts:detail', pk=contact.pk)
    else:
        # GET request - display form with current contact data
        form = ContactForm(instance=contact)
    
    context = {
        'form': form,
        'contact': contact,
        'title': 'Modifier le contact',
    }
    
    return render(request, 'contacts/contact_form.html', context)


@login_required
def contact_delete(request, pk):
    """
    Handle contact deletion with confirmation.
    
    Displays a confirmation page for GET requests and processes the
    deletion for POST requests. This two-step process prevents
    accidental deletions.
    
    Args:
        request: HTTP request object
        pk: Primary key of the contact to delete
        
    Returns:
        HttpResponse: Confirmation page (GET) or redirect to list (POST)
        
    Raises:
        Http404: If contact doesn't exist or doesn't belong to current user
    """
    # Ensure contact exists and belongs to current user
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Confirmed deletion - remove contact and redirect
        contact_name = contact.name  # Store name for success message
        contact.delete()
        
        messages.success(request, f'Contact "{contact_name}" supprimé avec succès.')
        return redirect('contacts:list')
    
    # GET request - show confirmation page
    context = {
        'contact': contact,
    }
    
    return render(request, 'contacts/contact_confirm_delete.html', context)