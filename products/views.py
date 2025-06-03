from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count, Q
from .models import Product, ProductVariant, Category
from reviews.models import Review  # import ici, pas dans méthode

def home_view(request):
    latest_products = Product.objects.filter(status='active').order_by('-created_at')[:8]
    categories = Category.objects.filter(parent__isnull=True).order_by('name')
    return render(request, 'home.html', {
        'latest_products': latest_products,
        'categories': categories,
    })


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().filter(status='active').select_related('vendor', 'category')

        category_slug = self.kwargs.get('category_slug') or self.request.GET.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            # Inclure la catégorie + ses enfants directs (pas récursif, pas MPTT)
            queryset = queryset.filter(Q(category=category) | Q(category__parent=category))

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))

        vendor_slug = self.request.GET.get('vendor')
        if vendor_slug:
            queryset = queryset.filter(vendor__slug=vendor_slug)

        size = self.request.GET.get('size')
        if size:
            queryset = queryset.filter(variants__size__iexact=size).distinct()

        color = self.request.GET.get('color')
        if color:
            queryset = queryset.filter(variants__color__iexact=color).distinct()

        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)

        material = self.request.GET.get('material')
        if material:
            queryset = queryset.filter(material=material)

        valid_sort_fields = ['price', '-price', 'name', '-name', '-created_at', 'created_at']
        sort_by = self.request.GET.get('sort_by', '-created_at')
        if sort_by not in valid_sort_fields:
            sort_by = '-created_at'
        queryset = queryset.order_by(sort_by)

        queryset = queryset.prefetch_related('images', 'variants')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Liste des catégories racines
        context['categories'] = Category.objects.filter(parent__isnull=True).order_by('name')

        context['all_colors'] = ProductVariant.objects.filter(
            product__status='active'
        ).values_list('color', flat=True).distinct().order_by('color')

        context['all_sizes'] = ProductVariant.objects.values_list('size', flat=True).distinct().order_by('size')

        context['conditions'] = Product.CONDITION_CHOICES
        context['materials'] = Product.MATERIAL_CHOICES

        request_get = self.request.GET
        context['current_query'] = request_get.get('q', '')
        context['current_sort_by'] = request_get.get('sort_by', '-created_at')
        context['current_size'] = request_get.get('size', '')
        context['current_color'] = request_get.get('color', '')
        context['current_condition'] = request_get.get('condition', '')
        context['current_material'] = request_get.get('material', '')
        context['current_vendor_slug'] = request_get.get('vendor', '')

        category_slug = self.kwargs.get('category_slug') or request_get.get('category_slug')
        context['current_category'] = get_object_or_404(Category, slug=category_slug) if category_slug else None

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # Annotation sans filtre is_approved (attention)
        return Product.objects.prefetch_related('images', 'variants').annotate(
            average_rating=Avg('reviews__rating'),
            total_reviews=Count('reviews')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['reviews'] = product.reviews.filter(is_approved=True).order_by('-created_at')
        context['related_products'] = Product.objects.filter(
            category=product.category
        ).exclude(pk=product.pk).order_by('?')[:4]
        return context
