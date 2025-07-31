# cart/urls.py
from django.urls import path
from . import views # Importe les vues de l'application cart
app_name = 'cart'
urlpatterns = [
    # Chemins pour les opérations sur le panier
    
    path('', views.cart_detail_view, name='cart_detail'), # Affiche le contenu du panier
    path('add/<int:variant_id>/', views.add_to_cart_view, name='add_to_cart'), # Ajoute un produit au panier
    path('remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'), # Supprime un article du panier
    path('update/<int:item_id>/', views.update_cart_view, name='update_cart'), # Met à jour la quantité d'un article
    path('clear/', views.clear_cart_view, name='clear_cart'),
    path('total/', views.cart_total_view, name='cart_total'),
    path('apply-discount/', views.apply_discount_view, name='apply_discount'),
    path('remove-discount/', views.remove_discount_view, name='remove_discount'),
    
]