import uuid
from django.urls import path
from carts.views import cart_add, cart_change, cart_remove
from . import views

app_name = 'carts'

urlpatterns = [
    path('cart_add/<slug:product_slug>', cart_add, name='cart_add'),
    path('cart_change/<int:cart_id>/', cart_change, name='cart_change'),
    path('cart_remove/<int:cart_id>', cart_remove, name='cart_remove'),
    path('cart/set-order-type/', views.set_order_type, name='set_order_type'),
    path('count/', views.cart_count, name='cart_count'),
]
