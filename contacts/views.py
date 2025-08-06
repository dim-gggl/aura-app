# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Contact
from .forms import ContactForm


@login_required
def contact_list(request):
    contacts = Contact.objects.filter(user=request.user)
    # Filtres
    search = request.GET.get('search', '')
    contact_type = request.GET.get('type', '')
    
    if search:
        contacts = contacts.filter(
            Q(name__icontains=search) |
            Q(address__icontains=search) |
            Q(email__icontains=search) |
            Q(notes__icontains=search)
        )
    
    if contact_type:
        contacts = contacts.filter(contact_type=contact_type)
    
    contacts = contacts.order_by('name')
    
    # Pagination
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'contacts': page_obj,
        'contact_types': Contact.CONTACT_TYPES,
        'current_filters': {
            'search': search,
            'type': contact_type,
        }
    }
    
    return render(request, 'contacts/contact_list.html', context)

@login_required
def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, 'Contact ajouté avec succès.')
            return redirect('contacts:list')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'title': 'Ajouter un contact',
    }
    
    return render(request, 'contacts/contact_form.html', context)

@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    return render(request, 'contacts/contact_detail.html', {'contact': contact})


@login_required
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact modifié avec succès.')
            return redirect('contacts:detail', pk=contact.pk)
    else:
        form = ContactForm(instance=contact)
    
    context = {
        'form': form,
        'contact': contact,
        'title': 'Modifier le contact',
    }
    
    return render(request, 'contacts/contact_form.html', context)

@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contact supprimé avec succès.')
        return redirect('contacts:list')
    
    return render(request, 'contacts/contact_confirm_delete.html', {'contact': contact})
