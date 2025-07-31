from django.contrib import admin
from .models import CustomUser, ContactMessage
from django.contrib.auth.admin import UserAdmin


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    ordering = ('-created_at',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Administration personnalisée pour le modèle CustomUser.
    Ajoute le champ 'is_seller' à la vue admin.
    """
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_seller',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_seller')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'is_seller')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_seller',)}),
    )