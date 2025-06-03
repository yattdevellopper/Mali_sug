# vendors/admin.py
from django.contrib import admin
from .models import Vendor # Assurez-vous que le modèle Vendor est correctement importé

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    """
    Administration simplifiée pour le modèle Vendor.
    Affiche les champs essentiels et permet une recherche basique.
    """
    # Champs à afficher dans la liste des vendeurs
    list_display = ('name', 'user', 'status', 'created_at') # Supprimé 'updated_at' pour simplifier
    
    # Champs sur lesquels la recherche est possible
    search_fields = ('name', 'user__username', 'contact_email') 
    
    # Génère automatiquement le slug à partir du nom du vendeur
    prepopulated_fields = {'slug': ('name',)} 

    # Note : Les options comme list_filter, raw_id_fields, fieldsets, et readonly_fields
    # ont été supprimées pour une version plus simple de l'administration.
