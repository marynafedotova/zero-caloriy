from carts.models import Cart

def get_user_carts(request):
    if not request.session.session_key:
        request.session.create()
    return Cart.objects.filter(session_key=request.session.session_key)


def calculate_delivery_cost(total_price):
    """
    Логіка:
    < 2000 грн — доставка недоступна (або за домовленістю, уточніть цей момент)
    2000 - 3999 грн — 200 грн
    >= 4000 грн — 0 грн
    """
    if total_price < 2000:
        return None  # Сигнал, що сума замала для таксі
    elif 2000 <= total_price < 4000:
        return 200
    else:
        return 0

