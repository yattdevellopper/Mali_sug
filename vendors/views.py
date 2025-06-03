# vendors/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils.text import slugify
from django.db.models import Sum, Count
from decimal import Decimal
# from uuid import uuid4 # Non utilisé dans la logique actuelle, mais peut être utile pour d'autres types de slugs uniques

from .models import Vendor
from products.models import Product
from orders.models import OrderItem
from products.forms import ProductForm, ProductVariantFormSet, ProductImageFormSet


# --- Vues Publiques ---

class VendorDetailView(DetailView):
    """
    Vue pour la page publique d'une boutique de vendeur.
    Affiche les informations du vendeur et ses produits actifs.
    """
    model = Vendor
    template_name = 'vendors/vendor_detail.html'
    context_object_name = 'vendor'
    slug_url_kwarg = 'vendor_slug'

    def get_queryset(self):
        return super().get_queryset().filter(status='active').select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.get_object()
        context['products'] = vendor.products.filter(status='active').order_by('-created_at')
        return context

# --- Vues du Tableau de Bord Vendeur ---

class VendorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Affiche le tableau de bord pour un vendeur connecté.
    Présente des statistiques clés et des liens de gestion.
    """
    template_name = 'vendors/dashboard.html'

    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.is_seller and \
               hasattr(self.request.user, 'vendor_profile') and \
               self.request.user.vendor_profile.status == 'active'

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, "Vous devez être connecté pour accéder au tableau de bord vendeur.")
            return redirect('accounts:login')
        messages.error(self.request, "Vous n'êtes pas un vendeur actif ou votre profil est en attente de validation.")
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            vendor_profile = self.request.user.vendor_profile 
        except Vendor.DoesNotExist:
            messages.error(self.request, "Profil vendeur introuvable pour cet utilisateur.")
            return context 

        context['vendor_profile'] = vendor_profile

        total_sales = OrderItem.objects.filter(
            vendor=vendor_profile,
            order__is_paid=True
        ).aggregate(Sum('price_at_purchase'))['price_at_purchase__sum'] or Decimal('0.00')
        context['total_sales'] = total_sales

        product_count = Product.objects.filter(vendor=vendor_profile, status='active').count()
        context['product_count'] = product_count

        pending_orders_count = OrderItem.objects.filter(
            vendor=vendor_profile,
            order__status__in=['pending', 'processing']
        ).values('order').distinct().count() 
        context['pending_orders_count'] = pending_orders_count

        vendor_products = Product.objects.filter(vendor=vendor_profile).order_by('-created_at')[:5]
        context['vendor_products'] = vendor_products
        
        return context

# --- Vues de Gestion des Produits par le Vendeur ---

class VendorProductListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Product
    template_name = 'vendors/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self.request.user, 'vendor_profile') and self.request.user.vendor_profile.status == 'active'

    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user.vendor_profile).order_by('-created_at')


class VendorProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Vue pour la création d'un nouveau produit par le vendeur.
    Gère le formulaire principal du produit, les variantes et les images.
    """
    model = Product
    form_class = ProductForm
    template_name = 'vendors/product_form.html'
    success_url = reverse_lazy('vendors:vendor_dashboard')

    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.is_seller and \
               hasattr(self.request.user, 'vendor_profile') and \
               self.request.user.vendor_profile.status == 'active'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['variants_formset'] = ProductVariantFormSet(self.request.POST, prefix='variants')
            data['images_formset'] = ProductImageFormSet(self.request.POST, self.request.FILES, prefix='images')
        else:
            data['variants_formset'] = ProductVariantFormSet(prefix='variants')
            data['images_formset'] = ProductImageFormSet(prefix='images')
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        variants_formset = context['variants_formset']
        images_formset = context['images_formset']

        with transaction.atomic():
            form.instance.vendor = self.request.user.vendor_profile
            
            # --- Logique pour assurer l'unicité du slug lors de la création ---
            original_slug = slugify(form.instance.name)
            unique_slug = original_slug
            num = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{original_slug}-{num}"
                num += 1
            form.instance.slug = unique_slug
            # --- FIN Logique slug ---
            
            self.object = form.save()

            if variants_formset.is_valid():
                variants_formset.instance = self.object
                variants_formset.save()
            else:
                messages.error(self.request, "Erreur dans les informations des variantes. Veuillez corriger.")
                return self.form_invalid(form) 

            if images_formset.is_valid():
                images_formset.instance = self.object
                images_formset.save()
            else:
                messages.error(self.request, "Erreur lors du téléchargement des images. Veuillez corriger.")
                return self.form_invalid(form)
        
        messages.success(self.request, "Votre produit a été créé avec succès !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Veuillez corriger les erreurs dans le formulaire du produit.")
        return super().form_invalid(form)


class VendorProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Vue pour la modification d'un produit existant par le vendeur.
    Préremplit le formulaire avec les données du produit, de ses variantes et images.
    """
    model = Product
    form_class = ProductForm
    template_name = 'vendors/product_form.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'
    success_url = reverse_lazy('vendors:vendor_dashboard')

    def test_func(self):
        product = self.get_object()
        return self.request.user.is_authenticated and \
               self.request.user.is_seller and \
               hasattr(self.request.user, 'vendor_profile') and \
               self.request.user.vendor_profile.status == 'active' and \
               product.vendor == self.request.user.vendor_profile

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['variants_formset'] = ProductVariantFormSet(self.request.POST, prefix='variants', instance=self.object)
            data['images_formset'] = ProductImageFormSet(self.request.POST, self.request.FILES, prefix='images', instance=self.object)
        else:
            data['variants_formset'] = ProductVariantFormSet(prefix='variants', instance=self.object)
            data['images_formset'] = ProductImageFormSet(prefix='images', instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        variants_formset = context['variants_formset']
        images_formset = context['images_formset']

        with transaction.atomic():
            # Pour la mise à jour, nous ne modifions le slug que si le nom a changé
            # et si le nouveau slug entre en conflit avec un autre produit (pas le produit actuel)
            if form.instance.name != self.object.name: # Si le nom a changé
                original_slug = slugify(form.instance.name)
                unique_slug = original_slug
                num = 1
                # Vérifier l'unicité par rapport à TOUS les produits SAUF celui que nous sommes en train de modifier
                while Product.objects.filter(slug=unique_slug).exclude(pk=self.object.pk).exists():
                    unique_slug = f"{original_slug}-{num}"
                    num += 1
                form.instance.slug = unique_slug
            
            self.object = form.save() # Sauvegarde les modifications du produit principal

            # Valide et sauvegarde les modifications des variantes
            if variants_formset.is_valid():
                variants_formset.instance = self.object
                variants_formset.save()
            else:
                messages.error(self.request, "Erreur dans les informations des variantes. Veuillez corriger.")
                return self.form_invalid(form)

            # Valide et sauvegarde les modifications des images
            if images_formset.is_valid():
                images_formset.instance = self.object
                images_formset.save()
            else:
                messages.error(self.request, "Erreur lors du téléchargement des images. Veuillez corriger.")
                return self.form_invalid(form)
        
        messages.success(self.request, "Votre produit a été mis à jour avec succès !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Veuillez corriger les erreurs dans le formulaire du produit.")
        return super().form_invalid(form)


class VendorProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'vendors/product_confirm_delete.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'
    success_url = reverse_lazy('vendors:vendor_dashboard')

    def test_func(self):
        product = self.get_object()
        return self.request.user.is_authenticated and \
               self.request.user.is_seller and \
               hasattr(self.request.user, 'vendor_profile') and \
               self.request.user.vendor_profile.status == 'active' and \
               product.vendor == self.request.user.vendor_profile

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f"Le produit '{self.get_object().name}' a été supprimé avec succès.")
        return super().delete(request, *args, **kwargs)
