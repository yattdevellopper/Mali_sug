# reviews/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # Pour les vues fonctionnelles
from django.contrib.auth.mixins import LoginRequiredMixin # Pour les vues basées sur les classes
from django.contrib import messages
from django.urls import reverse_lazy # Utile pour les redirections nommées
from django.views.generic import ListView # Pour la liste des avis utilisateur

from products.models import Product # Pour lier les avis aux produits
# from orders.models import OrderItem # N'est plus nécessaire si la vérification d'achat est supprimée
from .forms import ReviewForm # Assurez-vous d'avoir ce fichier forms.py
from .models import Review # Importe le modèle Review


@login_required
def add_review_view(request, product_slug):
    """
    Permet à un utilisateur de laisser un avis sur un produit.
    L'utilisateur doit être connecté. La vérification d'achat est supprimée.
    """
    product = get_object_or_404(Product, slug=product_slug)

    # # ANCIENNE LOGIQUE (COMMENTÉE/SUPPRIMÉE) : Vérification si l'utilisateur a acheté le produit
    # has_purchased = OrderItem.objects.filter(
    #     order__user=request.user,
    #     product_variant__product=product,
    #     order__status__in=['shipped', 'delivered']
    # ).exists()
    # if not has_purchased:
    #     messages.error(request, "Vous devez avoir acheté ce produit pour laisser un avis.")
    #     return redirect('products:product_detail', slug=product.slug)

    # Vérification si l'utilisateur a déjà laissé un avis pour ce produit
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, "Vous avez déjà laissé un avis pour ce produit. Vous pouvez le modifier si vous le souhaitez.")
        # Redirige vers la vue d'édition de l'avis existant
        return redirect('reviews:edit_review', product_slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_approved = False # Un nouvel avis est généralement non approuvé par défaut
            review.save()
            messages.success(request, "Merci pour votre avis ! Il sera visible après modération.")
            return redirect('products:product_detail', slug=product.slug)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ReviewForm()
    
    # Le template pour ajouter un avis
    return render(request, 'reviews/add_review.html', {'form': form, 'product': product})


@login_required
def edit_review_view(request, product_slug):
    """
    Permet à un utilisateur de modifier son avis existant sur un produit.
    """
    product = get_object_or_404(Product, slug=product_slug)
    review = get_object_or_404(Review, product=product, user=request.user) # Récupère l'avis de l'utilisateur pour ce produit

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review) # Passe l'instance de l'avis pour la modification
        if form.is_valid():
            form.save()
            review.is_approved = False # Remet à non approuvé pour re-modération après modification
            review.save()
            messages.success(request, "Votre avis a été mis à jour. Il sera visible à nouveau après modération.")
            return redirect('products:product_detail', slug=product.slug)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ReviewForm(instance=review) # Pré-remplit le formulaire avec l'avis existant
    
    # Le template pour éditer un avis
    return render(request, 'reviews/edit_review.html', {'form': form, 'product': product, 'review': review})

@login_required
def delete_review_view(request, product_slug):
    """
    Permet à un utilisateur de supprimer son avis sur un produit.
    """
    product = get_object_or_404(Product, slug=product_slug)
    review = get_object_or_404(Review, product=product, user=request.user) # Récupère l'avis de l'utilisateur pour ce produit

    if request.method == 'POST':
        review.delete()
        messages.info(request, "Votre avis a été supprimé.")
        return redirect('products:product_detail', slug=product.slug) # Redirige vers la page du produit
    
    # Le template de confirmation de suppression
    return render(request, 'reviews/confirm_delete_review.html', {'product': product, 'review': review})

class UserReviewsListView(LoginRequiredMixin, ListView):
    """
    Affiche la liste de tous les avis laissés par l'utilisateur connecté.
    """
    model = Review 
    template_name = 'reviews/user_reviews_list.html' # Chemin correct du template
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        # Récupère tous les avis de l'utilisateur connecté, triés par date de création
        return Review.objects.filter(user=self.request.user).order_by('-created_at')
