from goods.models import Restaurant
from goods.models import Category
from carts.utils import get_user_carts


def all_restaurants_processor(request):

    
 
    user_carts = get_user_carts(request)
    cart_total = user_carts.total_prace() 
    

    delivery_cost = request.session.get('delivery_cost', 0)


    terminal_id = request.session.get('terminal_id')
    selected_restaurant = None
    
    if terminal_id:
        selected_restaurant = Restaurant.objects.filter(id=terminal_id).first()
    
    return {
        'all_restaurants': Restaurant.objects.all(),
        'selected_restaurant': selected_restaurant,
        'cart_total_price': cart_total,
        'delivery_cost': delivery_cost,
        'full_total_sum': cart_total + delivery_cost, 
    }



def categories_processor(request):
    return {
        'all_categories': Category.objects.all()
    }