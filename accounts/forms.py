# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser # Assurez-vous que votre modèle User est importé ici

class CustomUserCreationForm(UserCreationForm):
    """
    Formulaire de création d'utilisateur personnalisé.
    Utilise le modèle User personnalisé de votre application accounts.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser # Utilise votre modèle User personnalisé
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'is_seller',) # Ajoutez les champs supplémentaires de votre modèle User si nécessaire

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des widgets ou ajout d'attributs HTML
        self.fields['email'].required = True # Rendez l'e-mail obligatoire
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Votre adresse email'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Votre prénom'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Votre nom'})
        self.fields['is_seller'].widget.attrs.update({'class': 'form-check-input'})

class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})