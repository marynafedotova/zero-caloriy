from goods.models import Restaurant


def all_restaurants_processor(request):
    restaurants = Restaurant.objects.all()
    return {
        'all_restaurants': restaurants
    }