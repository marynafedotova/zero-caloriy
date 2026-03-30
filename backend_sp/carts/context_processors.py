from carts.utils import get_user_carts

def cart_info(request):
    carts = get_user_carts(request)
    total_quantity = sum(item.quantity for item in carts)
    return {
        'user_cart_total_quantity': total_quantity
    }