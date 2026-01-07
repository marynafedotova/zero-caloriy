from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from goods.models import Product
from carts.models import Cart
from carts.utils import get_user_carts


# def cart_add(request, product_slug):
#     product = get_object_or_404(Product, slug=product_slug)
    
#     carts = Cart.objects.filter(session_key=request.session.session_key, product=product)

#     if carts.exists():
#         cart = carts.first()
#         if cart:
#             cart.quantity += 1
#             cart.save()
#         else:
#             Cart.objects.create(session_key=request.session.session_key, product=product, quantity=1)


#     return redirect(request.META.get('HTTP_REFERER', '/'))


def cart_add(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    

    if not request.session.session_key:
        request.session.create()
    
    key = request.session.session_key
    action = request.POST.get('action', 'plus')


    cart, created = Cart.objects.get_or_create(
        session_key=key, 
        product=product,
        defaults={'quantity': 0} 
    )

    if action == 'plus':
        cart.quantity += 1
        cart.save()
    elif action == 'minus':
        if cart.quantity > 1:
            cart.quantity -= 1
            cart.save()
        else:
            cart.delete()

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else '/')




def cart_change(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id)
    
    if request.method == 'POST':
        action = request.POST.get('action') 
        quantity = request.POST.get('quantity') 

        if action == 'plus':
            cart.quantity += 1
        elif action == 'minus':
            if cart.quantity > 1:
                cart.quantity -= 1
            else:
                cart.delete()
                return redirect(request.META.get('HTTP_REFERER', '/'))
        elif quantity and quantity.isdigit():
            cart.quantity = int(quantity)
        
        cart.save()
        messages.success(request, f"Кількість товару {cart.product.name} змінено.")
    
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else '/')


def cart_remove(request, cart_id):

    cart = Cart.objects.get(id=cart_id)
    cart.delete()

    referer = request.META.get('HTTP_REFERER')
    
    return redirect(referer if referer else '/')