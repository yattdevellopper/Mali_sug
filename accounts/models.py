from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Modèle d'utilisateur personnalisé étendant le modèle AbstractUser de Django.
    Permet d'ajouter des champs spécifiques à votre application.
    """
    # Ajoutez des champs supplémentaires ici si nécessaire, par exemple:
    # phone_number = models.CharField(max_length=15, blank=True, null=True)
    # address = models.TextField(blank=True, null=True)

    # Indique si l'utilisateur est un vendeur.
    # Sera utilisé pour rediriger vers le tableau de bord vendeur ou acheteur.
    is_seller = models.BooleanField(default=False)

    # Vous pouvez ajouter un champ pour le profil picture si vous voulez
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    class Meta:
        verbose_name = "Utilisateur Personnalisé"
        verbose_name_plural = "Utilisateurs Personnalisés"

    def __str__(self):
        return self.username
    
class ContactMessage(models.Model):
    """
    Modèle pour stocker les messages de contact.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.name} ({self.email})"