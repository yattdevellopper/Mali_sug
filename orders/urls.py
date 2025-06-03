# orders/urls.py
from django.urls import path
from . import views # Importe les vues de l'application orders

app_name = 'orders' # Bonne pratique pour les espaces de noms d'URL

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('my-orders/', views.UserOrderHistoryView.as_view(), name='user_orders_list'),
    path('<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
]
