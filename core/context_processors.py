def theme_context(request):
    # default if no page or not logged in
    default_theme = 'light'

    if request.user.is_authenticated:
        # page is a nullable OneToOneField → may be None
        page = request.user.page
        theme = page.theme if page else default_theme
    else:
        theme = default_theme

    return {'current_theme': theme}
