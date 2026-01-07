from django import template
from carts.models import Cart
from carts.utils import get_user_carts

register = template.Library()

@register.simple_tag()
def user_carts(request):
    return get_user_carts(request) 

@register.simple_tag
def get_cart_quantity(product, request):
    if not request.session.session_key:
        return 0
    
    cart_item = Cart.objects.filter(
        session_key=request.session.session_key, 
        product=product
    ).first()
    
    return cart_item.quantity if cart_item else 0