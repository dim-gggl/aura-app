def theme_context(request):
    # default if no page or not logged in
    default_theme = 'elegant'

    if request.user.is_authenticated:
        try:
            # page is a nullable OneToOneField → may be None
            profile = request.user.profile
            theme = profile.theme if profile else default_theme
        except AttributeError:
            theme = default_theme
    else:
        theme = default_theme

    return {'current_theme': theme}