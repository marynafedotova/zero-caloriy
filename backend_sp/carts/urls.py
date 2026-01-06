import uuid
from django.urls import path
from carts.views import cart_add, cart_change, cart_remove


app_name = 'carts'

urlpatterns = [
    path('cart_add/<uuid:product_id>', cart_add, name='cart_add'),
    path('cart_change/<uuid:product_id>', cart_change, name='cart_change'),
    path('cart_remove/<uuid:product_id>', cart_remove, name='cart_remove'),
]
