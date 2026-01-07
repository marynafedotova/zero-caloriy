from carts.models import Cart

def get_user_carts(request):
    if not request.session.session_key:
        request.session.create()
    return Cart.objects.filter(session_key=request.session.session_key)