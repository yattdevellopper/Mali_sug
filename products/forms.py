# products/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductVariant, ProductImage, Category # Assurez-vous d'importer Category aussi

class ProductForm(forms.ModelForm):
    """
    Formulaire principal pour la création et la modification d'un produit.
    """
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'material', 'condition', 'status']
        # 'vendor' et 'slug' seront gérés automatiquement par la vue
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Description détaillée'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'material': forms.Select(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nom du produit',
            'description': 'Description',
            'price': 'Prix de base',
            'category': 'Catégorie',
            'material': 'Matière',
            'condition': 'État du produit',
            'status': 'Statut (Brouillon/Actif)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Assurez-vous que les catégories sont bien chargées
        self.fields['category'].queryset = Category.objects.all().order_by('name')


# Formset pour les variantes (taille, couleur, stock)
ProductVariantFormSet = inlineformset_factory(
    Product, # Modèle parent
    ProductVariant, # Modèle enfant
    fields=['size', 'color', 'price_override', 'stock', 'sku'],
    extra=1, # Nombre de formulaires vides à afficher initialement
    can_delete=True, # Permet de supprimer des variantes existantes
    widgets={
        'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Taille (ex: S, M, 38)'}),
        'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Couleur (ex: Rouge, Noir)'}),
        'price_override': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Laisser vide si même prix que le produit'}),
        'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU (Optionnel)'}),
    },
    labels={
        'size': 'Taille',
        'color': 'Couleur',
        'price_override': 'Prix Spécifique',
        'stock': 'Stock',
        'sku': 'SKU',
    }
)

# Formset pour les images
ProductImageFormSet = inlineformset_factory(
    Product, # Modèle parent
    ProductImage, # Modèle enfant
    fields=['image', 'is_main', 'order'],
    extra=1,
    can_delete=True,
    widgets={
        'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
    },
    labels={
        'image': 'Image',
        'is_main': 'Image principale',
        'order': 'Ordre',
    }
)
