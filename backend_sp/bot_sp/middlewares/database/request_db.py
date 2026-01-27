from django.utils.timezone import now

from asgiref.sync import sync_to_async
from goods.models import Product
from users.models import User
from carts.models import Cart

@sync_to_async
def get_product():
    return list(Product.objects.all())

@sync_to_async
def add_to_cart_from_bot(chat_id, product_id):
    cart_item = Cart.objects.filter(chat_id=chat_id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(chat_id=chat_id, product_id=product_id, quantity=1)


@sync_to_async
def get_user_cart_details(chat_id):
    cart_items = list(Cart.objects.filter(chat_id=chat_id).select_related('product'))
    if not cart_items:
        return [], 0, 0
    
    qs = Cart.objects.filter(chat_id=chat_id)
    total_price = qs.total_prace()
    total_quantity = qs.total_quantity()
    
    return cart_items, total_price, total_quantity


@sync_to_async
def change_cart_quantity(chat_id, product_id, delta):
    item = Cart.objects.filter(chat_id=chat_id, product_id=product_id).first()
    if item:
        item.quantity += delta
        if item.quantity <= 0:
            item.delete()
            return None
        item.save()
        return item
    return None

@sync_to_async
def delete_cart_item(chat_id, product_id):
    """Видаляє конкретний товар з кошика конкретного користувача"""
    Cart.objects.filter(chat_id=chat_id, product_id=product_id).delete()

@sync_to_async
def clear_user_cart(chat_id):
    """Видаляє всі товари з кошика конкретного користувача"""
    Cart.objects.filter(chat_id=chat_id).delete()


@sync_to_async
def save_user_data(user_id, name, phone):
    user, created = User.objects.update_or_create(
        user_id=user_id,
        defaults={
            'first_name': name,
            'phone': phone,
            'last_activity': now(),
        }
    )
    return user