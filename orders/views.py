# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # Utilisé pour les vues fonctionnelles
from django.contrib.auth.mixins import LoginRequiredMixin # Utilisé pour les vues basées sur les classes
from django.contrib import messages
from django.db import transaction # Pour gérer les transactions atomiques
from decimal import Decimal # Pour les calculs de prix

# Importez les modèles nécessaires depuis l'application orders
from .models import Order, OrderItem, Payment, Commission
# Importez les modèles Cart et CartItem depuis l'application cart
from cart.models import Cart, CartItem # <--- Assurez-vous que cet import est correct

from products.models import ProductVariant # Nécessaire pour vérifier le stock et le prix des variantes

# Importez les vues génériques que vous utilisez
from django.views.generic import ListView, DetailView # ListView pour l'historique, DetailView pour le détail d'une commande


# Vue pour le processus de paiement (checkout)
@login_required # L'utilisateur doit être connecté pour passer commande
def checkout_view(request):
    """
    Gère le processus de paiement : affichage du formulaire d'adresse,
    validation et création de la commande.
    """
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        messages.warning(request, "Votre panier est vide. Veuillez ajouter des produits avant de passer commande.")
        # CORRECTION ICI : Ajout de 'cart:' à la redirection
        return redirect('cart:cart_detail')

    # Ici, vous devriez normalement intégrer un formulaire pour collecter
    # les adresses de livraison/facturation et d'autres informations de paiement.
    # Pour l'exemple, nous allons simuler un checkout simplifié.

    if request.method == 'POST':
        # --- Début de la transaction atomique ---
        # Si une erreur survient, toutes les modifications sont annulées.
        try:
            with transaction.atomic():
                # Créer une nouvelle commande
                order = Order.objects.create(
                    user=request.user,
                    total_amount=cart.get_total_price(),
                    status='pending', # En attente de confirmation de paiement
                    # Renseignez les adresses ici (pour l'exemple, des valeurs par défaut)
                    # En production, ces données viendraient d'un formulaire POST
                    shipping_address_line1="123 Rue de l'Exemple",
                    shipping_city="Ville Test",
                    shipping_zip_code="00000",
                    shipping_country="France",
                    billing_address_line1="123 Rue de l'Exemple",
                    billing_city="Ville Test",
                    billing_zip_code="00000",
                    billing_country="France",
                )

                # Transférer les articles du panier vers les articles de commande
                for cart_item in cart.items.all():
                    # Vérifier le stock une dernière fois avant de créer l'article de commande
                    if cart_item.product_variant.stock < cart_item.quantity:
                        raise Exception(f"Stock insuffisant pour {cart_item.product_variant.product.name} ({cart_item.product_variant.size}, {cart_item.product_variant.color}).")

                    OrderItem.objects.create(
                        order=order,
                        product_variant=cart_item.product_variant,
                        vendor=cart_item.product_variant.product.vendor, # Associer l'article au vendeur
                        quantity=cart_item.quantity,
                        price_at_purchase=cart_item.product_variant.get_price() # Enregistrez le prix au moment de l'achat
                    )
                    # Décrémentez le stock du produit
                    cart_item.product_variant.stock -= cart_item.quantity
                    cart_item.product_variant.save()

                # Supprimer tous les articles du panier après la création de la commande
                cart.items.all().delete()
                
                # Simuler une passerelle de paiement (ex: Stripe, PayPal)
                # Normalement, vous intégreriez votre logique de paiement ici (API d'une passerelle).
                # Si le paiement est réussi:
                payment_successful = True # Remplacer par le résultat réel de l'intégration de la passerelle
                if payment_successful:
                    order.status = 'processing' # La commande est en cours de traitement
                    order.is_paid = True
                    order.transaction_id = f"TXN_{order.id}_{order.created_at.timestamp()}" # Simule un ID de transaction
                    order.payment_method = "Simulated Payment" # Méthode de paiement simulée
                    order.save()

                    # Créer les commissions pour chaque OrderItem
                    for order_item in order.items.all():
                        # Ici, définissez votre logique de commission (ex: 15% du prix de vente)
                        commission_rate = Decimal('0.15') # 15%
                        commission_amount = order_item.get_total() * commission_rate
                        Commission.objects.create(
                            order_item=order_item,
                            vendor=order_item.vendor,
                            commission_rate=commission_rate,
                            commission_amount=commission_amount
                        )

                    messages.success(request, f"Votre commande #{order.id} a été passée avec succès !")
                    return redirect('orders:order_success', order_id=order.id) # Ajout de 'orders:'
                else:
                    messages.error(request, "Le paiement a échoué. Veuillez réessayer.")
                    order.status = 'pending' # Maintenir en attente si le paiement échoue
                    order.save()
                    return redirect('orders:checkout') # Ajout de 'orders:'

        except Exception as e:
            messages.error(request, f"Une erreur est survenue lors de la commande : {e}")
            return redirect('cart:cart_detail') # <--- CORRECTION ICI : Ajout de 'cart:'
    
    # Si la méthode n'est pas POST, afficher la page de checkout
    return render(request, 'orders/checkout.html', {'cart': cart})

# Vue de succès de commande
@login_required
def order_success_view(request, order_id):
    """
    Affiche une page de confirmation après qu'une commande ait été passée avec succès.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})

# Vue pour l'historique des commandes de l'utilisateur (maintenant une classe)
class UserOrderHistoryView(LoginRequiredMixin, ListView): 
    """
    Affiche la liste de toutes les commandes passées par l'utilisateur connecté.
    """
    model = Order
    template_name = 'orders/user_order_history.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        # Récupère toutes les commandes de l'utilisateur connecté, triées par date
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

# Vue pour les détails d'une commande spécifique de l'utilisateur
class OrderDetailView(LoginRequiredMixin, DetailView): 
    """
    Affiche les détails d'une commande spécifique pour l'utilisateur connecté.
    """
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id' # Le nom du paramètre d'ID dans l'URL

    def get_queryset(self):
        # S'assure que l'utilisateur ne peut voir que ses propres commandes
        return super().get_queryset().filter(user=self.request.user).prefetch_related('items__product_variant__product__vendor')
