from django.urls import path
from goods.views import catalog, product, cart

app_name = 'goods'

urlpatterns = [
    path('', catalog, name='catalog'),  # всі товари
    path('catalog/product/<slug:product_slug>/', product, name='product'),  # без групи
    path('cart/', cart, name='cart'),
    #path('menu/<slug:group_slug>/product/<slug:product_slug>/', product_detail, name='product_detail'),  # з групою
    #path('menu/<slug:slug>/', products_by_group, name='products_by_group'),  # товари групи
]
