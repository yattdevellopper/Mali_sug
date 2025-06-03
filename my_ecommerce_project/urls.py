"""
URL configuration for my_ecommerce_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# my_ecommerce_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Importez settings
from django.conf.urls.static import static # Importez static

# Importez votre vue d'accueil depuis l'application products
from products.views import home_view 

urlpatterns = [
    # Chemin d'accès pour l'interface d'administration de Django
    path('admin/', admin.site.urls),
    
    # Chemin d'accès pour la page d'accueil de votre site
    path('', home_view, name='home'), 

    # Inclure les URLs des applications de votre projet
    # Chaque application gère ses propres chemins d'accès
    path('accounts/', include('accounts.urls')), # URLs pour l'authentification et les comptes utilisateurs
    path('products/', include('products.urls')), # URLs pour l'affichage et la gestion des produits
    path('cart/', include('cart.urls')),         # URLs pour le panier d'achat
    path('orders/', include('orders.urls')),     # URLs pour la gestion des commandes
    path('vendors/', include('vendors.urls')),   # URLs pour les vendeurs et leur tableau de bord
    path('reviews/', include('reviews.urls')),   # URLs pour les avis et évaluations
]

# Servir les fichiers médias et statiques en mode développement
# Ces configurations sont essentielles pour afficher les images téléchargées
# et les fichiers CSS/JS pendant le développement.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

