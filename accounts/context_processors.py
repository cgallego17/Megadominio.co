from .models import Cart

def cart_context(request):
    """Context processor para el carrito de compras"""
    cart_items_count = 0
    
    if request.user.is_authenticated and hasattr(request.user, 'is_client') and request.user.is_client():
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = cart.get_items_count()
        except Cart.DoesNotExist:
            cart_items_count = 0
    
    return {
        'cart_items_count': cart_items_count
    } 