# reviews/admin.py
from django.contrib import admin
from .models import Review # Assurez-vous d'importer le modèle Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Administration minimale pour le modèle Review.
    Affiche les champs par défaut et permet une gestion basique.
    """
    # Champs à afficher dans la liste des avis (par défaut si non spécifié, mais explicité pour la clarté)
    list_display = ('product', 'user', 'rating', 'comment', 'is_approved', 'created_at')
    
    # Les options supplémentaires comme list_filter, search_fields, list_editable,
    # fieldsets et readonly_fields ont été supprimées pour une administration simplifiée.
