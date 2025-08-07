from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import json
# WeasyPrint sera importé uniquement quand nécessaire
import random
from datetime import datetime, timedelta

from .models import (
    Artwork, 
    Artist, 
    Collection, 
    Exhibition, 
    ArtworkPhoto, 
    WishlistItem, 
    ArtType, 
    Support, 
    Technique, 
    Keyword
)
from .forms import (
    ArtworkForm, 
    ArtistForm, 
    CollectionForm, 
    ExhibitionForm, 
    ArtworkPhotoFormSet, 
    WishlistItemForm
)
from .widgets import SelectOrCreateWidget, TagWidget
from .filters import ArtworkFilter


@login_required
def artwork_list(request):
    
    artworks = Artwork.objects.filter(user=request.user).prefetch_related("artists", "photos")
    artist_queryset = Artist.objects.filter(artwork__user=request.user).distinct()
    artwork_filter = ArtworkFilter(
        request.GET, 
        queryset=artworks
    )
    artwork_filter.form.fields['artists'].queryset = artist_queryset
    
    # Pagination
    paginator = Paginator(artworks, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    
    context = {
        "filter": artwork_filter,
        "page_obj": page_obj,
    }
    
    return render(request, "artworks/artwork_list.html", context)


@login_required
def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
    photos = artwork.photos.all()
    
    context = {
        "artwork": artwork,
        "photos": photos,
    }
    
    return render(request, "artworks/artwork_detail.html", context)


@login_required
def artwork_create(request):
    if request.method == "POST":
        form = ArtworkForm(request.POST, request.FILES, user=request.user)
        photo_formset = ArtworkPhotoFormSet(request.POST, request.FILES)
        
        if form.is_valid() and photo_formset.is_valid():
            artwork = form.save(commit=False)
            artwork.user = request.user
            artwork.save()
            form.save_m2m()
            
            # Sauvegarder le formset avec l'instance de l'œuvre
            photo_formset.instance = artwork
            photo_formset.save()
            
            messages.success(request, "Oeuvre ajoutée avec succès.")
            return redirect("artworks:detail", pk=artwork.pk)
    else:
        form = ArtworkForm(user=request.user)
        photo_formset = ArtworkPhotoFormSet()
    
    context = {
        "form": form,
        "photo_formset": photo_formset,
        "title": "Ajouter une œuvre",
    }
    
    return render(request, "artworks/artwork_form.html", context)


@login_required
def artwork_update(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
    
    if request.method == "POST":
        form = ArtworkForm(request.POST, instance=artwork, user=request.user)
        photo_formset = ArtworkPhotoFormSet(request.POST, request.FILES, instance=artwork)
        
        if form.is_valid() and photo_formset.is_valid():
            form.save()
            photo_formset.save()
            
            messages.success(request, "Œuvre modifiée avec succès.")
            return redirect("artworks:detail", pk=artwork.pk)
    else:
        form = ArtworkForm(instance=artwork, user=request.user)
        photo_formset = ArtworkPhotoFormSet(instance=artwork)
    
    context = {
        "form": form,
        "photo_formset": photo_formset,
        "artwork": artwork,
        "title": "Modifier l\"œuvre",
    }
    
    return render(request, "artworks/artwork_form.html", context)


@login_required
def artwork_delete(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
    
    if request.method == "POST":
        artwork.delete()
        messages.success(request, "Œuvre supprimée avec succès.")
        return redirect("artworks:list")
    
    return render(request, "artworks/artwork_confirm_delete.html", {"artwork": artwork})


@login_required
def random_suggestion(request):
    try:
        # Œuvres non exposées depuis plus de 6 mois
        six_months_ago = datetime.now().date() - timedelta(days=180)
        
        artworks = Artwork.objects.filter(
            user=request.user,
            current_location__in=["domicile", "stockage"]
        ).filter(
            Q(last_exhibited__lt=six_months_ago) | Q(last_exhibited__isnull=True)
        )
        
        if artworks.exists():
            # Convertir en liste pour éviter les problèmes avec random.choice sur un queryset
            artworks_list = list(artworks)
            suggested_artwork = random.choice(artworks_list)
            return render(request, "artworks/random_suggestion.html", {
                "artwork": suggested_artwork
            })
        else:
            return render(request, "artworks/random_suggestion.html", {
                "no_suggestion": True
            })
    except Exception as e:
        # En cas d'erreur, rediriger vers la liste des œuvres avec un message
        messages.error(request, "Une erreur est survenue lors de la génération de la suggestion.")
        return redirect("artworks:list")


@login_required
def artwork_export_html(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
    
    html_content = render_to_string("artworks/artwork_export.html", {
        "artwork": artwork,
        "photos": artwork.photos.all(),
    })
    
    response = HttpResponse(html_content, content_type="text/html")
    response["Content-Disposition"] = f"attachment; filename='artwork_{artwork.pk}.html'"
    
    return response


@login_required
def artwork_export_pdf(request, pk):
    # Import WeasyPrint localement pour éviter les erreurs au chargement du module
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as e:
        messages.error(request, 
            "L'export PDF n'est pas disponible. Les dépendances système de WeasyPrint ne sont pas installées.")
        return redirect("artworks:artwork_detail", pk=pk)
    
    artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
    
    html_content = render_to_string("artworks/artwork_export.html", {
        "artwork": artwork,
        "photos": artwork.photos.all(),
        "is_pdf": True,
    })
    
    pdf = HTML(string=html_content).write_pdf()
    
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename='artwork_{artwork.pk}.pdf'"
    
    return response

@login_required
def wishlist(request):
    items = WishlistItem.objects.filter(user=request.user)
    
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


@login_required
def artist_list(request):
    artists = Artist.objects.filter(artwork__user=request.user).distinct().annotate(
        artwork_count=Count("artwork")
    ).order_by("name")
    
    search = request.GET.get("search", "")
    if search:
        artists = artists.filter(name__icontains=search)
    
    paginator = Paginator(artists, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "search": search,
    }
    
    return render(request, "artworks/artist_list.html", context)


@login_required
def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    artworks = Artwork.objects.filter(artists=artist, user=request.user)
    
    context = {
        "artist": artist,
        "artworks": artworks,
    }
    
    return render(request, "artworks/artist_detail.html", context)


@login_required
def artist_create(request):
    if request.method == "POST":
        form = ArtistForm(request.POST)
        if form.is_valid():
            artist = form.save()
            messages.success(request, "Artiste ajouté avec succès.")
            return redirect("artworks:artist_detail", pk=artist.pk)
    else:
        form = ArtistForm()
    
    context = {
        "form": form,
        "title": "Ajouter un artiste",
    }
    
    return render(request, "artworks/artist_form.html", context)


@login_required
def artist_update(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    
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
        "title": "Modifier l\"artiste",
    }
    
    return render(request, "artworks/artist_form.html", context)


@require_POST
@login_required
def artist_create_ajax(request):
    """Créer un nouvel artiste via AJAX"""
    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        
        if not name:
            return JsonResponse({"error": "Le nom est requis"}, status=400)
        
        artist, created = Artist.objects.get_or_create(name=name)
        
        return JsonResponse({
            "success": True,
            "id": artist.pk,
            "name": artist.name,
            "created": created
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def collection_list(request):
    collections = Collection.objects.filter(user=request.user).annotate(
        artwork_count=Count("artwork")
    ).order_by("name")
    
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


@login_required
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    artworks = collection.artwork_set.all()
    
    context = {
        "collection": collection,
        "artworks": artworks,
    }
    
    return render(request, "artworks/collection_detail.html", context)


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


@login_required
def exhibition_list(request):
    exhibitions = Exhibition.objects.filter(user=request.user).annotate(
        artwork_count=Count("artwork")
    ).order_by("-start_date")
    
    search = request.GET.get("search", "")
    if search:
        exhibitions = exhibitions.filter(
            Q(name__icontains=search) | 
            Q(location__icontains=search) | 
            Q(description__icontains=search)
        )
    
    paginator = Paginator(exhibitions, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "search": search,
    }
    
    return render(request, "artworks/exhibition_list.html", context)


@login_required
def exhibition_detail(request, pk):
    exhibition = get_object_or_404(Exhibition, pk=pk, user=request.user)
    artworks = exhibition.artwork_set.all()
    
    context = {
        "exhibition": exhibition,
        "artworks": artworks,
    }
    
    return render(request, "artworks/exhibition_detail.html", context)


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
        form = ExhibitionForm()
    
    context = {
        "form": form,
        "title": "Créer une exposition",
    }
    
    return render(request, "artworks/exhibition_form.html", context)


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
        form = ExhibitionForm(instance=exhibition)
    
    context = {
        "form": form,
        "exhibition": exhibition,
        "title": "Modifier l\"exposition",
    }
    
    return render(request, "artworks/exhibition_form.html", context)


@login_required
def wishlist_delete(request, pk):
    item = get_object_or_404(WishlistItem, pk=pk, user=request.user)
    
    if request.method == "POST":
        item.delete()
        messages.success(request, "Œuvre retirée de la liste de souhaits.")
        return redirect("artworks:wishlist")
    
    return render(request, "artworks/wishlist_confirm_delete.html", {"item": item})

@require_POST
@login_required
def collection_create_ajax(request):
    """Créer une nouvelle collection via AJAX"""
    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        
        if not name:
            return JsonResponse({"error": "Le nom est requis"}, status=400)
        
        collection, created = Collection.objects.get_or_create(
            name=name,
            user=request.user,
            defaults={"description": ""}
        )
        
        return JsonResponse({
            "success": True,
            "id": collection.pk,
            "name": collection.name,
            "created": created
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
@login_required
def exhibition_create_ajax(request):
    """Créer une nouvelle exposition via AJAX"""
    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        
        if not name:
            return JsonResponse({"error": "Le nom est requis"}, status=400)
        
        exhibition, created = Exhibition.objects.get_or_create(
            name=name,
            user=request.user,
            defaults={"description": "", "location": ""}
        )
        
        return JsonResponse({
            "success": True,
            "id": exhibition.pk,
            "name": exhibition.name,
            "created": created
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
@login_required
def arttype_create_ajax(request):
    """Créer un nouveau type d"art via AJAX"""
    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        
        if not name:
            return JsonResponse({"error": "Le nom est requis"}, status=400)
        
        art_type, created = ArtType.objects.get_or_create(name=name)
        
        return JsonResponse({
            "success": True,
            "id": art_type.pk,
            "name": art_type.name,
            "created": created
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
@login_required
def support_create_ajax(request):
    """Créer un nouveau support via AJAX"""
    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        
        if not name:
            return JsonResponse({"error": "Le nom est requis"}, status=400)
        
        support, created = Support.objects.get_or_create(name=name)
        
        return JsonResponse({
            "success": True,
            "id": support.pk,
            "name": support.name,
            "created": created
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
@login_required
def technique_create_ajax(request):
    """Créer une nouvelle technique via AJAX"""
    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        
        if not name:
            return JsonResponse({"error": "Le nom est requis"}, status=400)
        
        technique, created = Technique.objects.get_or_create(name=name)
        
        return JsonResponse({
            "success": True,
            "id": technique.pk,
            "name": technique.name,
            "created": created
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def keyword_autocomplete(request):
    """Auto-complétion pour les mots-clés"""
    term = request.GET.get("term", "").strip()
    
    if len(term) < 2:
        return JsonResponse({"results": []})
    
    keywords = Keyword.objects.filter(name__icontains=term)[:10]
    
    results = [{"id": kw.pk, "text": kw.name} for kw in keywords]
    
    return JsonResponse({"results": results})

@require_POST
@login_required
def keyword_create_ajax(request):
    """Créer un nouveau mot-clé via AJAX"""
    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        if not name:
            return JsonResponse({"error": "Le nom est requis"}, status=400)
        keyword, created = Keyword.objects.get_or_create(name=name)
        return JsonResponse({
            "success": True,
            "id": keyword.pk,
            "name": keyword.name,
            "created": created
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Vues pour la gestion des entités de référence

@login_required
def arttype_list(request):
    """Liste des types d'art"""
    art_types = ArtType.objects.all().annotate(
        artwork_count=Count("artwork")
    ).order_by("name")
    
    search = request.GET.get("search", "")
    if search:
        art_types = art_types.filter(name__icontains=search)
    
    paginator = Paginator(art_types, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "search": search,
        "entity_name": "Type d'art",
        "entity_name_plural": "Types d'art",
        "create_url": "artworks:arttype_create",
    }
    
    return render(request, "artworks/reference_list.html", context)


@login_required
def arttype_create(request):
    """Créer un nouveau type d'art"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            art_type, created = ArtType.objects.get_or_create(name=name)
            if created:
                messages.success(request, f"Type d'art '{name}' créé avec succès.")
            else:
                messages.info(request, f"Type d'art '{name}' existe déjà.")
            return redirect("artworks:arttype_list")
        else:
            messages.error(request, "Le nom est requis.")
    
    context = {
        "title": "Ajouter un type d'art",
        "entity_name": "type d'art",
        "back_url": "artworks:arttype_list",
    }
    
    return render(request, "artworks/reference_form.html", context)


@login_required
def arttype_update(request, pk):
    """Modifier un type d'art"""
    art_type = get_object_or_404(ArtType, pk=pk)
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            if name != art_type.name:
                if ArtType.objects.filter(name=name).exists():
                    messages.error(request, f"Un type d'art avec le nom '{name}' existe déjà.")
                else:
                    art_type.name = name
                    art_type.save()
                    messages.success(request, "Type d'art modifié avec succès.")
                    return redirect("artworks:arttype_list")
            else:
                return redirect("artworks:arttype_list")
        else:
            messages.error(request, "Le nom est requis.")
    
    context = {
        "title": "Modifier le type d'art",
        "entity_name": "type d'art",
        "current_name": art_type.name,
        "back_url": "artworks:arttype_list",
    }
    
    return render(request, "artworks/reference_form.html", context)


@login_required
def arttype_delete(request, pk):
    """Supprimer un type d'art"""
    art_type = get_object_or_404(ArtType, pk=pk)
    
    if request.method == "POST":
        name = art_type.name
        art_type.delete()
        messages.success(request, f"Type d'art '{name}' supprimé avec succès.")
        return redirect("artworks:arttype_list")
    
    context = {
        "object": art_type,
        "entity_name": "type d'art",
        "back_url": "artworks:arttype_list",
    }
    
    return render(request, "artworks/reference_confirm_delete.html", context)


@login_required
def support_list(request):
    """Liste des supports"""
    supports = Support.objects.all().annotate(
        artwork_count=Count("artwork")
    ).order_by("name")
    
    search = request.GET.get("search", "")
    if search:
        supports = supports.filter(name__icontains=search)
    
    paginator = Paginator(supports, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "search": search,
        "entity_name": "Support",
        "entity_name_plural": "Supports",
        "create_url": "artworks:support_create",
    }
    
    return render(request, "artworks/reference_list.html", context)


@login_required
def support_create(request):
    """Créer un nouveau support"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            support, created = Support.objects.get_or_create(name=name)
            if created:
                messages.success(request, f"Support '{name}' créé avec succès.")
            else:
                messages.info(request, f"Support '{name}' existe déjà.")
            return redirect("artworks:support_list")
        else:
            messages.error(request, "Le nom est requis.")
    
    context = {
        "title": "Ajouter un support",
        "entity_name": "support",
        "back_url": "artworks:support_list",
    }
    
    return render(request, "artworks/reference_form.html", context)


@login_required
def support_update(request, pk):
    """Modifier un support"""
    support = get_object_or_404(Support, pk=pk)
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            if name != support.name:
                if Support.objects.filter(name=name).exists():
                    messages.error(request, f"Un support avec le nom '{name}' existe déjà.")
                else:
                    support.name = name
                    support.save()
                    messages.success(request, "Support modifié avec succès.")
                    return redirect("artworks:support_list")
            else:
                return redirect("artworks:support_list")
        else:
            messages.error(request, "Le nom est requis.")
    
    context = {
        "title": "Modifier le support",
        "entity_name": "support",
        "current_name": support.name,
        "back_url": "artworks:support_list",
    }
    
    return render(request, "artworks/reference_form.html", context)


@login_required
def support_delete(request, pk):
    """Supprimer un support"""
    support = get_object_or_404(Support, pk=pk)
    
    if request.method == "POST":
        name = support.name
        support.delete()
        messages.success(request, f"Support '{name}' supprimé avec succès.")
        return redirect("artworks:support_list")
    
    context = {
        "object": support,
        "entity_name": "support",
        "back_url": "artworks:support_list",
    }
    
    return render(request, "artworks/reference_confirm_delete.html", context)


@login_required
def technique_list(request):
    """Liste des techniques"""
    techniques = Technique.objects.all().annotate(
        artwork_count=Count("artwork")
    ).order_by("name")
    
    search = request.GET.get("search", "")
    if search:
        techniques = techniques.filter(name__icontains=search)
    
    paginator = Paginator(techniques, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "search": search,
        "entity_name": "Technique",
        "entity_name_plural": "Techniques",
        "create_url": "artworks:technique_create",
    }
    
    return render(request, "artworks/reference_list.html", context)


@login_required
def technique_create(request):
    """Créer une nouvelle technique"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            technique, created = Technique.objects.get_or_create(name=name)
            if created:
                messages.success(request, f"Technique '{name}' créée avec succès.")
            else:
                messages.info(request, f"Technique '{name}' existe déjà.")
            return redirect("artworks:technique_list")
        else:
            messages.error(request, "Le nom est requis.")
    
    context = {
        "title": "Ajouter une technique",
        "entity_name": "technique",
        "back_url": "artworks:technique_list",
    }
    
    return render(request, "artworks/reference_form.html", context)


@login_required
def technique_update(request, pk):
    """Modifier une technique"""
    technique = get_object_or_404(Technique, pk=pk)
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            if name != technique.name:
                if Technique.objects.filter(name=name).exists():
                    messages.error(request, f"Une technique avec le nom '{name}' existe déjà.")
                else:
                    technique.name = name
                    technique.save()
                    messages.success(request, "Technique modifiée avec succès.")
                    return redirect("artworks:technique_list")
            else:
                return redirect("artworks:technique_list")
        else:
            messages.error(request, "Le nom est requis.")
    
    context = {
        "title": "Modifier la technique",
        "entity_name": "technique",
        "current_name": technique.name,
        "back_url": "artworks:technique_list",
    }
    
    return render(request, "artworks/reference_form.html", context)


@login_required
def technique_delete(request, pk):
    """Supprimer une technique"""
    technique = get_object_or_404(Technique, pk=pk)
    
    if request.method == "POST":
        name = technique.name
        technique.delete()
        messages.success(request, f"Technique '{name}' supprimée avec succès.")
        return redirect("artworks:technique_list")
    
    context = {
        "object": technique,
        "entity_name": "technique",
        "back_url": "artworks:technique_list",
    }
    
    return render(request, "artworks/reference_confirm_delete.html", context)


@login_required
def keyword_list(request):
    """Liste des mots-clés"""
    keywords = Keyword.objects.all().annotate(
        artwork_count=Count("artwork")
    ).order_by("name")
    
    search = request.GET.get("search", "")
    if search:
        keywords = keywords.filter(name__icontains=search)
    
    paginator = Paginator(keywords, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "search": search,
        "entity_name": "Mot-clé",
        "entity_name_plural": "Mots-clés",
        "create_url": "artworks:keyword_create",
    }
    
    return render(request, "artworks/reference_list.html", context)


@login_required
def keyword_create(request):
    """Créer un nouveau mot-clé"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            keyword, created = Keyword.objects.get_or_create(name=name)
            if created:
                messages.success(request, f"Mot-clé '{name}' créé avec succès.")
            else:
                messages.info(request, f"Mot-clé '{name}' existe déjà.")
            return redirect("artworks:keyword_list")
        else:
            messages.error(request, "Le nom est requis.")
    
    context = {
        "title": "Ajouter un mot-clé",
        "entity_name": "mot-clé",
        "back_url": "artworks:keyword_list",
    }
    
    return render(request, "artworks/reference_form.html", context)


@login_required
def keyword_update(request, pk):
    """Modifier un mot-clé"""
    keyword = get_object_or_404(Keyword, pk=pk)
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            if name != keyword.name:
                if Keyword.objects.filter(name=name).exists():
                    messages.error(request, f"Un mot-clé avec le nom '{name}' existe déjà.")
                else:
                    keyword.name = name
                    keyword.save()
                    messages.success(request, "Mot-clé modifié avec succès.")
                    return redirect("artworks:keyword_list")
            else:
                return redirect("artworks:keyword_list")
        else:
            messages.error(request, "Le nom est requis.")
    
    context = {
        "title": "Modifier le mot-clé",
        "entity_name": "mot-clé",
        "current_name": keyword.name,
        "back_url": "artworks:keyword_list",
    }
    
    return render(request, "artworks/reference_form.html", context)


@login_required
def keyword_delete(request, pk):
    """Supprimer un mot-clé"""
    keyword = get_object_or_404(Keyword, pk=pk)
    
    if request.method == "POST":
        name = keyword.name
        keyword.delete()
        messages.success(request, f"Mot-clé '{name}' supprimé avec succès.")
        return redirect("artworks:keyword_list")
    
    context = {
        "object": keyword,
        "entity_name": "mot-clé",
        "back_url": "artworks:keyword_list",
    }
    
    return render(request, "artworks/reference_confirm_delete.html", context)
