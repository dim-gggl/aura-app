def theme_context(request):
    # default if no page or not logged in
    default_theme = 'elegant'

    if request.user.is_authenticated:
        try:
            # page is a nullable OneToOneField → may be None
            profile = request.user.profile
            if profile and profile.theme:
                theme = profile.theme
            else:
                # Create profile if it doesn't exist
                from core.models import UserProfile
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                theme = profile.theme if profile.theme else default_theme
        except AttributeError:
            theme = default_theme
    else:
        theme = default_theme

    return {'current_theme': theme}