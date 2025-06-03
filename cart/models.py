# cart/models.py
from django.db import models
from django.conf import settings # Pour accéder au modèle User personnalisé (AUTH_USER_MODEL)
from products.models import ProductVariant # Pour lier les articles du panier aux variantes de produits
from decimal import Decimal # Pour des calculs de prix précis


class Cart(models.Model):
    """
    Représente le panier d'achat d'un utilisateur.
    Peut être lié à un utilisateur connecté ou à une session anonyme.
    """
    # Lien vers l'utilisateur si connecté. Nullable pour les utilisateurs anonymes.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name="Utilisateur"
    )
    # ID de session pour les utilisateurs non connectés. Unique pour éviter les doublons.
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True, # Assure qu'un ID de session n'est lié qu'à un seul panier
        verbose_name="ID de session"
    )
    # Date de création du panier
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    # Date de la dernière mise à jour du panier
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"
        # Ajoutez une contrainte pour s'assurer qu'un panier a soit un utilisateur, soit un session_id, mais pas les deux à la fois
        # ou qu'il ne peut pas être sans les deux.
        # Note: Cette validation est souvent mieux gérée au niveau du formulaire ou de la vue lors de la création/récupération du panier.
        # Pour une unicité stricte, on peut ajouter:
        # unique_together = ('user', 'session_id') # Non, car l'un ou l'autre peut être null.
        # Plutôt, gérer la logique dans la vue: si user est présent, session_id est ignoré/nullifié.

    def __str__(self):
        if self.user:
            return f"Panier de {self.user.username}"
        elif self.session_id:
            return f"Panier de session {self.session_id[:8]}..."
        return "Panier anonyme"

    def get_total_price(self):
        """
        Calcule le prix total de tous les articles dans le panier.
        """
        return sum(item.get_total() for item in self.items.all())

    def get_total_items(self):
        """
        Calcule le nombre total d'articles (quantité cumulée) dans le panier.
        """
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """
    Représente un article individuel dans un panier.
    """
    # Lien vers le panier auquel cet article appartient
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Panier"
    )
    # Lien vers la variante de produit ajoutée au panier
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="Variante de produit"
    )
    # Quantité de cette variante de produit dans le panier
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    # Prix de la variante au moment où elle a été ajoutée au panier.
    # Ceci est important pour éviter que les changements de prix futurs n'affectent les paniers existants.
    price_at_addition = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix à l'ajout"
    )
    # Date d'ajout ou de dernière mise à jour de l'article dans le panier
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Ajouté le")

    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"
        # Unicité: une seule variante de produit par panier pour éviter les doublons
        unique_together = ('cart', 'product_variant')

    def __str__(self):
        return f"{self.quantity} x {self.product_variant.product.name} ({self.product_variant.size}/{self.product_variant.color})"

    def get_total(self):
        """
        Calcule le prix total pour cet article du panier (quantité * prix à l'ajout).
        """
        return self.price_at_addition * self.quantity

