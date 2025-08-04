from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_type', 'email', 'phone', 'user']
    list_filter = ['contact_type', 'user']
    search_fields = ['name', 'email', 'address', 'notes']