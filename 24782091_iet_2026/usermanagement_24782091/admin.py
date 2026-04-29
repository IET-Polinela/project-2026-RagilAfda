from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_member', 'is_staff', 'is_superuser')

admin.site.register(CustomUser, CustomUserAdmin)