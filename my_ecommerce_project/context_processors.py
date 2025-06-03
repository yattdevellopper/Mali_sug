# my_ecommerce_project/context_processors.py
from products.models import Category
# my_ecommerce_project/my_ecommerce_project/context_processors.py
from cart.models import Cart # Importe le modèle Cart depuis l'application cart

def cart_total_quantity(request):
    """
    Processeur de contexte qui ajoute le nombre total d'articles dans le panier
    au contexte de chaque requête.
    """
    total_quantity = 0
    try:
        if request.user.is_authenticated:
            # Pour les utilisateurs connectés, récupère le panier associé à l'utilisateur
            cart = Cart.objects.get(user=request.user)
        else:
            # Pour les utilisateurs non connectés, utilise l'ID de session
            session_id = request.session.session_key
            if not session_id:
                request.session.save() # S'assure qu'une session existe
                session_id = request.session.session_key
            cart = Cart.objects.get(session_id=session_id)
        
        # Calcule la somme des quantités de tous les articles dans le panier
        for item in cart.items.all():
            total_quantity += item.quantity
    except Cart.DoesNotExist:
        # Si le panier n'existe pas encore, la quantité est 0
        total_quantity = 0
    except Exception as e:
        # Gérer d'autres erreurs potentielles (par exemple, problèmes de base de données)
        print(f"Erreur lors du calcul de la quantité du panier : {e}")
        total_quantity = 0 # Assurez-vous que la quantité est 0 en cas d'erreur

    return {'cart_total_quantity': total_quantity}




def categories_context(request):
    return {
        'categories': Category.objects.filter(parent__isnull=True).order_by('name'),
    }