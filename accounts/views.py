# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

from .forms import CustomUserCreationForm, UserProfileForm
from core.models import UserProfile


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a UserProfile for the new user
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Compte créé avec succès. Bienvenue!')
            return redirect('core:dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    # Make sure a profile exists for the user, create if not
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, 
                                 request.FILES, 
                                 instance=profile, 
                                 user=request.user)
        
        if form.is_valid():
            # Gérer la suppression de la photo de profil
            if request.POST.get('remove_picture'):
                if profile.profile_picture:
                    profile.profile_picture.delete(save=False)
                profile.profile_picture = None
            
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    # Force load of all theme choices
    theme_choices = UserProfile.THEME_CHOICES
    
    context = {
        'form': form,
        'theme_choices': theme_choices
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_test(request):
    # Make sure a profile exists for the user, create if not
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, 
                                 request.FILES, 
                                 instance=profile, 
                                 user=request.user)
        
        # Débogage
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        
        if form.is_valid():
            # Gérer la suppression de la photo de profil
            if request.POST.get('remove_picture'):
                if profile.profile_picture:
                    profile.profile_picture.delete(save=False)
                profile.profile_picture = None
            
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('accounts:profile_test')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    return render(request, 'accounts/profile_simple.html', {'form': form})

