from django.db import models
from accounts.models import CustomUser
from products.models import Product

class Review(models.Model):
    """
    Représente un avis (évaluation et commentaire) pour un produit.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Produit")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews', verbose_name="Acheteur")
    
    # Note de 1 à 5
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Évaluation")
    
    comment = models.TextField(blank=True, null=True, verbose_name="Commentaire")
    
    # Possibilité pour l'acheteur d'ajouter des photos à son avis
    # review_image = models.ImageField(upload_to='review_images/', blank=True, null=True, verbose_name="Photo de l'avis")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Pour la modération des avis
    is_approved = models.BooleanField(default=False, verbose_name="Approuvé par l'administrateur")

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        # Empêche un utilisateur de laisser plus d'un avis par produit
        unique_together = ('product', 'user')
        ordering = ['-created_at'] # Les avis les plus récents en premier

    def __str__(self):
        return f"Avis de {self.user.username} sur {self.product.name} ({self.rating} étoiles)"