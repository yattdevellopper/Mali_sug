from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ExportActionMixin
from import_export import resources

from .models import Category, Product, ProductImage, ProductVariant


# Ressources import/export
class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        skip_unchanged = True
        report_skipped = True


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category


class ProductVariantResource(resources.ModelResource):
    class Meta:
        model = ProductVariant


# Admin catégorie
@admin.register(Category)
class CategoryAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class = CategoryResource
    list_display = ['name', 'parent']
    search_fields = ['name']
    list_filter = ['parent']


# Admin produit
@admin.register(Product)
class ProductAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class = ProductResource
    list_display = [
        'name', 'category', 'vendor_link', 'price', 'status',
        'condition', 'created_at', 'main_image_tag', 'stock_total'
    ]
    list_filter = ['status', 'condition', 'category', 'vendor', 'created_at']
    search_fields = ['name', 'description', 'slug', 'vendor__name']
    ordering = ['-created_at']
    readonly_fields = ['main_image_tag']

    def main_image_url(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image:
            return main_image.image.url
        return None

    def main_image_tag(self, obj):
        url = self.main_image_url(obj)
        if url:
            return format_html('<img src="{}" width="60" style="object-fit:cover; border-radius:4px;" />', url)
        return "—"
    main_image_tag.short_description = "Image principale"
    main_image_tag.allow_tags = True

    def vendor_link(self, obj):
        if obj.vendor:
            return format_html(
                '<a href="/admin/vendors/vendor/{}/change/">{}</a>',
                obj.vendor.id, obj.vendor.name
            )
        return "—"
    vendor_link.short_description = "Vendeur"

    def stock_total(self, obj):
        return obj.get_total_stock()
    stock_total.short_description = "Stock total"


# Admin images produit
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_main', 'order']
    list_filter = ['is_main']
    search_fields = ['product__name']


# Admin variantes produit
@admin.register(ProductVariant)
class ProductVariantAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class = ProductVariantResource
    list_display = ['product', 'color', 'size', 'price_override', 'stock', 'sku']
    search_fields = ['product__name', 'color', 'size', 'sku']
    list_filter = ['color', 'size']
    ordering = ['product', 'size', 'color']
