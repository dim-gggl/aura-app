"""
URL configuration for the core application.

This module defines the URL patterns for the core functionality of the Aura
art collection management application. These URLs provide the main navigation
structure and entry points for users.

URL Structure:
- / : Homepage (redirects to dashboard for authenticated users)
- /dashboard/ : Main user dashboard with overview and statistics
- /search/ : Global search functionality across all user data

The core URLs serve as the foundation for the application's navigation
and provide the main user interface entry points.
"""

from django.urls import path
from . import views

# Namespace for the core app - allows {% url 'core:home' %} in templates
app_name = 'core'

urlpatterns = [
    # ========================================
    # MAIN APPLICATION URLS
    # ========================================
    
    # Homepage - entry point for the application
    # Redirects authenticated users to dashboard, shows welcome page for anonymous users
    path('', views.home, name='home'),
    
    # Main dashboard - central hub for authenticated users
    # Displays statistics, recent activity, and quick access to features
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Global search - comprehensive search across all user data
    # Searches artworks, contacts, and notes simultaneously
    path('search/', views.search, name='search'),
    
    # Health check endpoint for monitoring and load balancers
    # Used by Docker health checks and monitoring systems
    path('health/', views.health_check, name='health'),
    
    # Web App Manifest (served as template to inject hashed static URLs)
    path('site.webmanifest', views.site_manifest, name='manifest'),
]