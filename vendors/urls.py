# vendors/urls.py
from django.urls import path
from . import views # Importe les vues de l'application vendors

app_name = 'vendors' # <--- AJOUTEZ CETTE LIGNE !

urlpatterns = [
    # CORRECTION ICI : Utilisation de .as_view() pour la vue basée sur une classe
    path('dashboard/', views.VendorDashboardView.as_view(), name='vendor_dashboard'), # Tableau de bord principal du vendeur
    
    # Assurez-vous que ces chemins d'accès sont également corrects et utilisent .as_view() pour les classes
    path('products/', views.VendorProductListView.as_view(), name='vendor_product_list'), # Liste des produits du vendeur
    path('products/add/', views.VendorProductCreateView.as_view(), name='vendor_product_add'), # Ajouter un nouveau produit
    path('products/edit/<slug:product_slug>/', views.VendorProductUpdateView.as_view(), name='vendor_product_edit'), # Modifier un produit existant
    path('products/delete/<slug:product_slug>/', views.VendorProductDeleteView.as_view(), name='vendor_product_delete'), # Supprimer un produit
    
    path('<slug:vendor_slug>/', views.VendorDetailView.as_view(), name='vendor_detail'), # Page de profil public du vendeur
]
