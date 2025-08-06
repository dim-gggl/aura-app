# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Note
from .forms import NoteForm

@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user)
    
    # Filtres
    search = request.GET.get('search', '')
    favorites_only = request.GET.get('favorites', '')
    
    if search:
        notes = notes.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )
    
    if favorites_only:
        notes = notes.filter(is_favorite=True)
    
    notes = notes.order_by('-updated_at')
    
    # Pagination
    paginator = Paginator(notes, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notes': page_obj,
        'current_filters': {
            'search': search,
            'favorites': favorites_only,
        }
    }
    
    return render(request, 'notes/note_list.html', context)

@login_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Note créée avec succès.')
            return redirect('notes:list')
    else:
        form = NoteForm()
    
    context = {
        'form': form,
        'title': 'Nouvelle note',
    }
    
    return render(request, 'notes/note_form.html', context)

@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    
    return render(request, 'notes/note_detail.html', {'note': note})

@login_required
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note modifiée avec succès.')
            return redirect('notes:detail', pk=note.pk)
    else:
        form = NoteForm(instance=note)
    
    context = {
        'form': form,
        'note': note,
        'title': 'Modifier la note',
    }
    
    return render(request, 'notes/note_form.html', context)

@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note supprimée avec succès.')
        return redirect('notes:list')
    
    return render(request, 'notes/note_confirm_delete.html', {'note': note})

@login_required
def note_toggle_favorite(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.is_favorite = not note.is_favorite
    note.save()
    
    status = "ajoutée aux" if note.is_favorite else "retirée des"
    messages.success(request, f'Note {status} favoris.')
    
    return redirect('notes:detail', pk=note.pk)
