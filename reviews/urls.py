# reviews/urls.py
from django.urls import path
from . import views

app_name = 'reviews' # Espace de noms pour cette application

urlpatterns = [
    # URL pour ajouter un avis à un produit
    path('add/<slug:product_slug>/', views.add_review_view, name='add_review'),
    
    # URL pour la liste des avis de l'utilisateur (vue basée sur une classe)
    path('my-reviews/', views.UserReviewsListView.as_view(), name='user_reviews_list'),
    
    # URL pour modifier un avis existant
    path('edit/<slug:product_slug>/', views.edit_review_view, name='edit_review'),
    
    # URL pour supprimer un avis existant
    path('delete/<slug:product_slug>/', views.delete_review_view, name='delete_review'),
]
