from goods.models import Restaurant
from goods.models import Category


def all_restaurants_processor(request):
    restaurants = Restaurant.objects.all()
    return {
        'all_restaurants': restaurants
    }



def categories_processor(request):
    return {
        'all_categories': Category.objects.all()
    }