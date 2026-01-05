from asgiref.sync import sync_to_async
from goods.models import Product

@sync_to_async
def get_product():
    return list(Product.objects.all())