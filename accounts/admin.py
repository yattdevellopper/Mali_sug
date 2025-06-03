from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Administration personnalisée pour le modèle CustomUser.
    Ajoute le champ 'is_seller' à la vue admin.
    """
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_seller',)}), # Ajoutez 'is_seller' au fieldset
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_seller')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'is_seller')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)