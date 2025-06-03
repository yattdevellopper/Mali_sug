from django.db import models
from accounts.models import CustomUser
from products.models import ProductVariant
from vendors.models import Vendor

# Modèle pour le panier de l'utilisateur
class Cart(models.Model):
    """
    Représente le panier d'achat d'un utilisateur.
    Un utilisateur peut avoir un seul panier actif.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    # Pour les utilisateurs non connectés, vous pouvez utiliser une session ID
    session_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"

    def __str__(self):
        if self.user:
            return f"Panier de {self.user.username}"
        return f"Panier (Session: {self.session_id[:8]})"

    def get_total_price(self):
        """ Calcule le prix total de tous les articles dans le panier. """
        # Ensure that item.get_total() handles potential None values as well
        return sum(item.get_total() for item in self.items.all())

class CartItem(models.Model):
    """
    Représente un article individuel dans le panier d'achat.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    # Optionnel: Enregistrer le prix au moment de l'ajout au panier si les prix peuvent changer
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        # Assure qu'une seule variante de produit peut être ajoutée par panier
        unique_together = ('cart', 'product_variant')
        verbose_name = "Article du Panier"
        verbose_name_plural = "Articles du Panier"

    def __str__(self):
        return f"{self.quantity} x {self.product_variant.product.name} ({self.product_variant.size}, {self.product_variant.color})"

    def get_total(self):
        """ Calcule le prix total pour cet article du panier. """
        # Use price_at_addition if available, otherwise fallback to product_variant's price
        # Ensure the price is not None before multiplication
        price = self.price_at_addition
        if price is None:
            # Fallback to the current product variant price if price_at_addition is not set
            # Make sure product_variant and its get_price() method exist and return a number
            price = self.product_variant.get_price() if hasattr(self.product_variant, 'get_price') else 0

        # If price is still None or not a number, default to 0 for calculation
        price = price if price is not None else 0
        
        return price * self.quantity

# Modèle pour une commande client
class Order(models.Model):
    """
    Représente une commande passée par un acheteur.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name="Acheteur")
    
    # Informations de livraison
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100, blank=True, null=True) # Pour les pays avec des états/provinces
    shipping_zip_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=20, blank=True, null=True)

    # Informations de facturation (peut être identique à l'expédition)
    billing_address_line1 = models.CharField(max_length=255)
    billing_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100, blank=True, null=True)
    billing_zip_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100)

    # Statut de la commande
    STATUS_CHOICES = [
        ('pending', 'En attente de paiement'),
        ('processing', 'En cours de traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
        ('refunded', 'Remboursée'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Informations de paiement
    transaction_id = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name="ID de transaction du paiement")
    payment_method = models.CharField(max_length=50, blank=True, null=True) # Ex: Stripe, PayPal, etc.
    is_paid = models.BooleanField(default=False)
    
    # CORRECTION: Permettre à total_amount d'être NULL et blank initialement
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant total de la commande",
        null=True,  # Permet à la colonne d'être NULL dans la base de données
        blank=True  # Permet au champ d'être vide dans les formulaires (comme l'admin)
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande #{self.id} de {self.user.username if self.user else 'Invité'}"

    def get_items_by_vendor(self):
        """
        Organise les articles de la commande par vendeur.
        Utile pour le traitement des commandes côté vendeur.
        """
        items_by_vendor = {}
        # Assurez-vous que 'items' est le related_name de ForeignKey de OrderItem vers Order
        for item in self.items.all(): 
            vendor = item.product_variant.product.vendor
            if vendor not in items_by_vendor:
                items_by_vendor[vendor] = []
            items_by_vendor[vendor].append(item)
        return items_by_vendor


# Modèle pour les articles individuels d'une commande
class OrderItem(models.Model):
    """
    Représente un article individuel inclus dans une commande.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='ordered_items') # Pour faciliter la gestion des commissions/paiements
    quantity = models.PositiveIntegerField(default=1)
    # This field *should* always have a value, but we'll add a default for safety
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

    # Statut spécifique à l'article de commande (ex: en traitement, expédié, livré par ce vendeur)
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours (Vendeur)'),
        ('shipped', 'Expédié (Vendeur)'),
        ('delivered', 'Livré (Vendeur)'),
        ('returned', 'Retourné'),
        ('refunded', 'Remboursé (Article)'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        verbose_name = "Article de Commande"
        verbose_name_plural = "Articles de Commande"
        # Optional: unique_together = ('order', 'product_variant') si un article ne peut pas être dupliqué dans une commande
        ordering = ['order', 'product_variant__product__name']

    def __str__(self):
        return f"{self.quantity} x {self.product_variant.product.name} (Order #{self.order.id})"

    def get_total(self):
        """ Calcule le prix total pour cet article de commande. """
        # Defensive check: Ensure price_at_purchase is not None
        # If price_at_purchase is None, default to 0 to prevent TypeError
        price = self.price_at_purchase if self.price_at_purchase is not None else 0
        return price * self.quantity

# Modèle pour les paiements (historique et état des transactions)
class Payment(models.Model):
    """
    Enregistre les détails des transactions de paiement.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=255, unique=True, verbose_name="ID de transaction")
    payment_method = models.CharField(max_length=50, verbose_name="Méthode de paiement")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant payé")
    currency = models.CharField(max_length=3, default='XOF', verbose_name="Devise") # Par exemple, XOF pour le Franc CFA
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']

    def __str__(self):
        return f"Paiement pour Commande #{self.order.id} - {self.amount} {self.currency}"

# Modèle pour la gestion des commissions et des versements aux vendeurs
class Commission(models.Model):
    """
    Enregistre la commission due à la plateforme pour chaque article vendu.
    """
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='commission')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='commissions_earned')
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taux de commission (%)") # Ex: 0.15 pour 15%
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant de la commission")
    is_paid_to_vendor = models.BooleanField(default=False, verbose_name="Montant vendeur versé")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Commission"
        verbose_name_plural = "Commissions"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commission pour {self.order_item} - {self.commission_amount}"