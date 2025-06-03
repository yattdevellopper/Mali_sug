# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse # Importe JsonResponse pour les réponses AJAX
from products.models import ProductVariant
from .models import Cart, CartItem
from decimal import Decimal

# Vue pour afficher le panier
def cart_detail_view(request):
    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.save()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    
    # Assurez-vous que le prix de chaque article est à jour
    for item in cart.items.all():
        item.price_at_addition = item.product_variant.get_price() 
        item.save()

    return render(request, 'cart/cart_detail.html', {'cart': cart})

# Vue pour ajouter un article au panier
def add_to_cart_view(request, variant_id):
    if request.method == 'POST':
        product_variant = get_object_or_404(ProductVariant, id=variant_id)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            message = "Quantité invalide."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': message})
            messages.error(request, message)
            return redirect('products:product_detail', slug=product_variant.product.slug)

        if quantity <= 0:
            message = "La quantité doit être au moins de 1."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': message})
            messages.error(request, message)
            return redirect('products:product_detail', slug=product_variant.product.slug)

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.save()
                session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_id=session_id)

        if product_variant.stock < quantity:
            message = f"Stock insuffisant pour {product_variant.product.name} ({product_variant.size}, {product_variant.color}). Stock disponible : {product_variant.stock}."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': message})
            messages.error(request, message)
            return redirect('products:product_detail', slug=product_variant.product.slug)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_variant=product_variant)
            new_quantity = cart_item.quantity + quantity
            
            if new_quantity > product_variant.stock:
                message = f"Impossible d'ajouter plus de {product_variant.stock - cart_item.quantity} articles de {product_variant.product.name}. Le stock maximum serait dépassé."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': message})
                messages.error(request, message)
                return redirect('products:product_detail', slug=product_variant.product.slug)
            
            cart_item.quantity = new_quantity
            cart_item.price_at_addition = product_variant.get_price() 
            cart_item.save()
            message = f"Quantité de {product_variant.product.name} mise à jour dans votre panier."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': message, 'cart_total_quantity': cart.get_total_items()})
            messages.success(request, message)
        except CartItem.DoesNotExist:
            CartItem.objects.create(
                cart=cart,
                product_variant=product_variant,
                quantity=quantity,
                price_at_addition=product_variant.get_price()
            )
            message = f"{product_variant.product.name} a été ajouté à votre panier."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': message, 'cart_total_quantity': cart.get_total_items()})
            messages.success(request, message)
        except Exception as e:
            message = f"Une erreur inattendue est survenue lors de l'ajout au panier : {e}"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': message})
            messages.error(request, message)
            return redirect('products:product_detail', slug=product_variant.product.slug)
        
        return redirect('cart:cart_detail')
    else:
        message = "Requête invalide pour ajouter au panier."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': message})
        messages.error(request, message)
        return redirect('products:product_list')

# Vue pour retirer un article du panier
def remove_from_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.user.is_authenticated:
        if cart_item.cart.user != request.user:
            messages.error(request, "Vous n'êtes pas autorisé à supprimer cet article.")
            return redirect('cart:cart_detail')
    else:
        if cart_item.cart.session_id != request.session.session_key:
            messages.error(request, "Vous n'êtes pas autorisé à supprimer cet article.")
            return redirect('cart:cart_detail')

    product_name = cart_item.product_variant.product.name
    cart_item.delete()
    messages.info(request, f"{product_name} a été retiré de votre panier.")
    return redirect('cart:cart_detail')

# Vue pour mettre à jour la quantité d'un article dans le panier
def update_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.user.is_authenticated:
        if cart_item.cart.user != request.user:
            messages.error(request, "Vous n'êtes pas autorisé à modifier cet article.")
            return redirect('cart:cart_detail')
    else:
        if cart_item.cart.session_id != request.session.session_key:
            messages.error(request, "Vous n'êtes pas autorisé à modifier cet article.")
            return redirect('cart:cart_detail')

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
            if quantity <= 0:
                messages.error(request, "La quantité doit être au moins de 1.")
            elif quantity > cart_item.product_variant.stock:
                messages.error(request, f"Stock insuffisant. Quantité maximale disponible : {cart_item.product_variant.stock}.")
            else:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, f"Quantité de {cart_item.product_variant.product.name} mise à jour.")
        except ValueError:
            messages.error(request, "Quantité invalide.")
    
    return redirect('cart:cart_detail')
