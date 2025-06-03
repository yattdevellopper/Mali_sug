# reviews/forms.py
from django import forms
from .models import Review # Make sure Review model is imported

class ReviewForm(forms.ModelForm):
    """
    Formulaire pour permettre aux utilisateurs d'ajouter ou de modifier un avis.
    """
    class Meta:
        model = Review
        # Les champs 'product' et 'user' seront remplis automatiquement dans la vue
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Partagez votre expérience avec ce produit...'}),
        }
        labels = {
            'rating': 'Votre évaluation',
            'comment': 'Votre commentaire',
        }