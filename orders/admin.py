# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem, Payment, Commission # Assurez-vous d'importer tous les modèles nécessaires

# ----- Inlines pour OrderAdmin -----

class OrderItemInline(admin.TabularInline):
    """
    Permet de gérer les articles d'une commande directement sur la page de la commande.
    """
    model = OrderItem
    extra = 0 # Pas de formulaire vide par défaut
    readonly_fields = ('product_variant', 'vendor', 'quantity', 'price_at_purchase', 'get_total') # Ces champs sont définis à la création
    fields = ('product_variant', 'vendor', 'quantity', 'price_at_purchase', 'get_total', 'status')

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = "Total Article"

# ----- Administration des modèles -----

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Administration pour le modèle Order.
    Gère les commandes et intègre les articles de commande et le paiement.
    """
    list_display = ('id', 'user', 'total_amount', 'status', 'is_paid', 'created_at')
    list_filter = ('status', 'is_paid', 'created_at', 'payment_method')
    search_fields = ('user__username', 'shipping_address_line1', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'total_amount', 'transaction_id', 'payment_method', 'is_paid') # Empêche la modification manuelle de ces champs critiques

    inlines = [OrderItemInline] # Affiche les articles de la commande directement dans l'admin

    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'total_amount', 'is_paid')
        }),
        ('Détails du Paiement', {
            'fields': ('transaction_id', 'payment_method'),
            'classes': ('collapse',)
        }),
        ('Adresse de Livraison', {
            'fields': ('shipping_address_line1', 'shipping_address_line2', 'shipping_city', 'shipping_state', 'shipping_zip_code', 'shipping_country', 'shipping_phone'),
        }),
        ('Adresse de Facturation', {
            'fields': ('billing_address_line1', 'billing_address_line2', 'billing_city', 'billing_state', 'billing_zip_code', 'billing_country'),
            'classes': ('collapse',) # Masque par défaut pour plus de clarté
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Administration pour le modèle Payment.
    """
    list_display = ('order', 'transaction_id', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__id', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'transaction_id', 'amount') # Empêche la modification manuelle des données de paiement


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    """
    Administration pour le modèle Commission.
    Permet de suivre les commissions générées et les paiements aux vendeurs.
    """
    list_display = ('order_item', 'vendor', 'commission_rate', 'commission_amount', 'is_paid_to_vendor', 'created_at', 'paid_at')
    list_filter = ('is_paid_to_vendor', 'vendor', 'created_at')
    search_fields = ('order_item__order__id', 'vendor__name')
    readonly_fields = ('created_at', 'commission_amount', 'order_item', 'vendor') # Le montant et l'article ne sont pas modifiables
