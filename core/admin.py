from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile


admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'created_at']
    list_filter = ['theme', 'created_at']
    search_fields = ['user__username', 'user__email']
