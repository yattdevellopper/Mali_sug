# products/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from decimal import Decimal
from django.db.models import Avg, Count
from vendors.models import Vendor

# Modèle pour les catégories de produits (sans mptt)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug", help_text="Un identifiant unique pour l'URL de la catégorie (ex: robes-ete)")
    description = models.TextField(blank=True, verbose_name="Description de la catégorie")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Image")

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Catégorie parente"
    )

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        full_path = [self.name]
        current = self
        while current.parent:
            full_path.insert(0, current.parent.name)
            current = current.parent
        return ' > '.join(full_path)


# Modèle pour les produits
class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Neuf avec étiquette'),
        ('likenew', 'Comme neuf (porté une ou deux fois)'),
        ('good', 'Bon état (quelques signes d\'usure)'),
        ('fair', 'État correct (usure visible)'),
        ('vintage', 'Vintage'),
    ]
    MATERIAL_CHOICES = [
        ('cotton', 'Coton'), ('polyester', 'Polyester'), ('silk', 'Soie'),
        ('wool', 'Laine'), ('denim', 'Denim'), ('leather', 'Cuir'),
        ('linen', 'Lin'), ('rayon', 'Rayonne'), ('spandex', 'Spandex'),
        ('blend', 'Mélange'), ('other', 'Autre')
    ]
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('pending', 'En attente de validation'),
        ('active', 'Actif'),
        ('archived', 'Archivé'),
        ('out_of_stock', 'En rupture de stock'),
    ]

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Vendeur"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Catégorie"
    )
    name = models.CharField(max_length=255, verbose_name="Nom du produit")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="Slug", help_text="Un identifiant unique pour l'URL du produit")
    description = models.TextField(verbose_name="Description détaillée du produit")

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de base")

    material = models.CharField(max_length=50, choices=MATERIAL_CHOICES, blank=True, verbose_name="Matière principale")
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='new', verbose_name="État du produit")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft', verbose_name="Statut du produit")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_price(self):
        return self.price

    def get_total_stock(self):
        return sum(variant.stock for variant in self.variants.all())

    def average_rating(self):
        from reviews.models import Review
        return self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0.0

    def total_reviews(self):
        from reviews.models import Review
        return self.reviews.filter(is_approved=True).count()


# Modèle pour les images de produits
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Produit")
    image = models.ImageField(upload_to='product_images/', verbose_name="Fichier image")
    is_main = models.BooleanField(default=False, verbose_name="Image principale")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Image de Produit"
        verbose_name_plural = "Images de Produits"
        ordering = ['order', '-is_main']

    def __str__(self):
        return f"Image for {self.product.name} (Main: {self.is_main})"


# Modèle pour les variantes de produits (taille, couleur, etc.)
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="Produit")

    size = models.CharField(max_length=50, blank=True, null=True, verbose_name="Taille")
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name="Couleur")

    price_override = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Laissez vide si le prix est le même que celui du produit de base."
    )

    stock = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="SKU (Stock Keeping Unit)")

    class Meta:
        unique_together = ('product', 'size', 'color')
        verbose_name = "Variante de Produit"
        verbose_name_plural = "Variantes de Produits"
        ordering = ['product', 'size', 'color']

    def __str__(self):
        return f"{self.product.name} ({self.color}, {self.size})"

    def get_price(self):
        return self.price_override if self.price_override is not None else self.product.price
