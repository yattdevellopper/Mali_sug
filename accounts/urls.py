# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views # Importe les vues d'authentification de Django
from . import views # Importe vos vues personnalisées (register, password_change, etc.)


app_name = 'accounts' # Définit l'espace de noms pour cette application

urlpatterns = [
    # Vue d'inscription personnalisée
    path('register/', views.register_view, name='register'),
    
    # Vues d'authentification de Django (Login et Logout)
    # Nous spécifions le template_name pour nous assurer que Django trouve vos templates personnalisés.
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # Redirige vers la page d'accueil après déconnexion
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'), 

    # Vues de gestion des mots de passe personnalisées (définies dans accounts/views.py)
    # Ces chemins d'accès appellent vos fonctions ou classes de vue directement.
    path('password_change/', views.password_change_view, name='password_change'),
    path('password_change/done/', views.password_change_done_view, name='password_change_done'),
    
    path('password_reset/', views.password_reset_view, name='password_reset'),
    path('password_reset/done/', views.password_reset_done_view, name='password_reset_done'),
    # uidb64 et token sont des paramètres nécessaires pour la réinitialisation
    path('reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete_view, name='password_reset_complete'),
]
