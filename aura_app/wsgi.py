"""
WSGI config for aura_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings by default, can be overridden by environment variable
# This ensures Railway and other deployment platforms use the correct settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aura_app.settings.production")

application = get_wsgi_application()
