"""
URL configuration for the accounts application.

This module defines comprehensive URL patterns for user account management,
including registration, authentication, profile management, and password
recovery. It combines custom views with Django's built-in authentication
views for a complete user account system.

URL Structure:
- Registration: /accounts/register/
- Authentication: /accounts/login/, /accounts/logout/
- Profile Management: /accounts/profile/
- Password Management: Complete password change and reset flow
- Development: Test endpoints for debugging

The URLs provide a complete user account management system with all
standard authentication features expected in modern web applications.
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

# Namespace for the accounts app - allows {% url 'accounts:login' %} in templates
app_name = "accounts"

urlpatterns = [
    # ========================================
    # CUSTOM ACCOUNT MANAGEMENT URLS
    # ========================================
    # User registration with custom form and automatic profile creation
    path("register/", views.register, name="register"),
    # User profile management (viewing and editing)
    path("profile/", views.profile, name="profile"),
    # (removed) Test/debug version of profile view
    # ========================================
    # DJANGO BUILT-IN AUTHENTICATION URLS
    # ========================================
    # Login and logout using Django's built-in views
    # These views use templates in registration/ directory
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", views.logout, name="logout"),
    # ========================================
    # PASSWORD MANAGEMENT URLS
    # ========================================
    # Password change for authenticated users
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    # Password reset flow for users who forgot their password
    # Step 1: Request password reset (enter email)
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    # Step 2: Confirmation that reset email was sent
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    # Step 3: Reset password using token from email
    # uidb64: Base64 encoded user ID, token: Password reset token
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Step 4: Confirmation that password was successfully reset
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

# Note: Django's built-in authentication views expect templates in specific locations:
# - registration/login.html
# - registration/password_change_form.html
# - registration/password_change_done.html
# - registration/password_reset_form.html
# - registration/password_reset_done.html
# - registration/password_reset_confirm.html
# - registration/password_reset_complete.html
