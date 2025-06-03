# cart/admin.py
from django.contrib import admin
from .models import Cart, CartItem # Importe les modèles Cart et CartItem

# Définir un Inline pour afficher les articles du panier directement dans l'admin du Panier
class CartItemInline(admin.TabularInline):
    """
    Permet d'éditer les articles du panier directement depuis la page d'édition du Panier.
    """
    model = CartItem
    extra = 0 # Ne pas afficher de formulaires vides supplémentaires par défaut
    fields = ['product_variant', 'quantity', 'price_at_addition', 'added_at']
    # CORRECTION ICI : 'price_at_addition' a été retiré de readonly_fields
    readonly_fields = ['added_at'] # Ce champ ne devrait pas être modifiable manuellement

# Définir l'interface d'administration pour le modèle Cart
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Personnalise l'affichage du modèle Panier dans l'interface d'administration.
    """
    list_display = ('id', 'user', 'session_id', 'created_at', 'updated_at', 'get_total_price', 'get_total_items')
    list_filter = ('created_at', 'updated_at', 'user')
    search_fields = ('user__username', 'session_id')
    readonly_fields = ('created_at', 'updated_at') # Ces champs sont auto-générés
    inlines = [CartItemInline] # Inclut les articles du panier directement dans l'édition du panier

    # Personnalisation de la méthode de recherche pour inclure les articles du panier
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            # Recherche par nom de produit dans les articles du panier
            queryset |= self.model.objects.filter(items__product_variant__product__name__icontains=search_term)
            # Recherche par SKU de variante
            queryset |= self.model.objects.filter(items__product_variant__sku__icontains=search_term)
            use_distinct = True
        return queryset, use_distinct

    # Méthodes personnalisées pour list_display
    def get_total_price(self, obj):
        return f"{obj.get_total_price():.2f} FCFA"
    get_total_price.short_description = "Prix Total"

    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = "Nb Articles"

# Définir l'interface d'administration pour le modèle CartItem (si vous voulez une vue séparée)
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Personnalise l'affichage du modèle Article du Panier dans l'interface d'administration.
    """
    list_display = ('cart', 'product_variant', 'quantity', 'price_at_addition', 'added_at', 'get_total')
    list_filter = ('added_at', 'cart__user', 'product_variant__product__category')
    search_fields = ('cart__user__username', 'product_variant__product__name', 'product_variant__sku')
    # CORRECTION ICI : 'price_at_addition' a été retiré de readonly_fields
    readonly_fields = ('added_at',)

    # Méthode personnalisée pour list_display
    def get_total(self, obj):
        return f"{obj.get_total():.2f} FCFA"
    get_total.short_description = "Total Article"
