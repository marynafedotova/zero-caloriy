from django.urls import path
from goods.views import catalog, product, cart, product_search, create_order_telegram

app_name = 'goods'

urlpatterns = [
    path('', catalog, name='catalog'),  # всі товари
    path('catalog/product/<slug:product_slug>/', product, name='product'),  # без групи
    path('cart/', cart, name='cart'),
    path('search/', product_search, name='search'),
    path('create-order/', create_order_telegram, name='create-order'),

]
