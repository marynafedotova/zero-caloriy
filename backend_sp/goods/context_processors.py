from goods.models import Restaurant
from goods.models import Category
from carts.utils import get_user_carts


def all_restaurants_processor(request):

    
 
    user_carts = get_user_carts(request)
    cart_total = user_carts.total_prace() 
    

    delivery_cost = request.session.get('delivery_cost', 0)
    
    return {
        'all_restaurants': Restaurant.objects.filter(is_active=True),
        'cart_total_price': cart_total,
        'delivery_cost': delivery_cost,
        'full_total_sum': cart_total + delivery_cost, 
    }


def categories_processor(request):
    return {
        'all_categories': Category.objects.all()
    }