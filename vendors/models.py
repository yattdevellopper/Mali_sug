from django.db import models
from accounts.models import CustomUser

class Vendor(models.Model):
    """
    Représente un profil de vendeur sur la marketplace.
    Chaque vendeur est lié à un utilisateur CustomUser.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='vendor_profile')
    name = models.CharField(max_length=255, unique=True, verbose_name="Nom de la boutique")
    slug = models.SlugField(unique=True, help_text="Un identifiant unique pour l'URL de la boutique (ex: ma-super-boutique)")
    description = models.TextField(blank=True, verbose_name="Description de la boutique")
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True, verbose_name="Logo de la boutique")
    contact_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True, verbose_name="Adresse de la boutique (optionnel)")
    
    # Politique de retour spécifique au vendeur
    return_policy = models.TextField(blank=True, verbose_name="Politique de retour du vendeur")

    # Statut du vendeur (ex: en attente d'approbation, actif, suspendu)
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('rejected', 'Rejeté'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Date d'inscription et de dernière mise à jour
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vendeur"
        verbose_name_plural = "Vendeurs"
        ordering = ['name'] # Ordonner les vendeurs par nom

    def __str__(self):
        return self.name