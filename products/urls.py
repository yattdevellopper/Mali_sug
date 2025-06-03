# products/urls.py
from django.urls import path
from . import views # Correctly imports your views module
app_name = 'products'
urlpatterns = [
    # Route for listing all products (e.g., /products/)
    # Uses ProductListView, which is a class-based view, so we call .as_view()
    path('', views.ProductListView.as_view(), name='product_list'),

    # Route for displaying a single product's details (e.g., /products/my-awesome-product-slug/)
    # Uses ProductDetailView, also a class-based view, requiring .as_view()
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Route for listing products filtered by category (e.g., /products/category/electronics/)
    # Reuses ProductListView, passing the category_slug via URL arguments
    path('category/<slug:category_slug>/', views.ProductListView.as_view(), name='product_list_by_category'),

    # Example: If you have an 'add to cart' URL within products app (can also be in a 'cart' app)
    # path('<slug:product_slug>/add-to-cart/', views.add_to_cart_view, name='add_to_cart'),
]