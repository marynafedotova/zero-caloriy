import os
from django.db.models import Sum
from django.core.cache import cache
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from goods.models import Product, Restaurant
from carts.models import Cart
from goods.services.syrve_client import SyrveClient
from goods.views import check_cart_for_stop_list
from carts.utils import get_user_carts, calculate_delivery_cost


def set_order_type(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error"}, status=405)

    order_type_key = request.POST.get('type')
    terminal_id = request.POST.get('terminal_id')

    ORDER_TYPE_MAPPING = {
        'DELIVERY': '49cf98d2-25ab-d404-a5a8-11eaffc7ce7f',
        'PICKUP':   '7bb5d30f-c8bc-d694-93a8-0d955e274921',
    }

    order_type_id = ORDER_TYPE_MAPPING.get(order_type_key)
    if not order_type_id:
        return JsonResponse({"status": "error", "message": "Невідомий тип"}, status=400)

    

    # очищаємо попередній стан
    request.session.pop('terminal_id', None)
    request.session.pop('delivery_cost', None)

    # DELIVERY — ЖОРСТКО ФІКСОВАНИЙ ТЕРМІНАЛ
    if order_type_key == 'DELIVERY':
        user_carts = get_user_carts(request)
        total = user_carts.total_prace()

        delivery_cost = calculate_delivery_cost(total)
       
        delivery_cost = 0 if delivery_cost is None else delivery_cost

        request.session['terminal_id'] = settings.DELIVERY_TERMINAL_ID
        request.session['delivery_cost'] = delivery_cost

    # PICKUP — ТЕРМІНАЛ ОБОВʼЯЗКОВИЙ З ФРОНТА
    elif order_type_key == 'PICKUP':
        if not terminal_id:
            return JsonResponse(
                {"status": "error", "message": "Оберіть точку самовивозу"},
                status=400
            )

        request.session['terminal_id'] = terminal_id
        request.session['delivery_cost'] = 0

    request.session['order_type'] = order_type_key
    request.session['order_type_id'] = order_type_id
    request.session.modified = True


    # --- ДОДАНА ПЕРЕВІРКА СТОП-ЛИСТА (ТІЛЬКИ ТУТ) ---
    terminal_id = request.session.get('terminal_id')
    carts = get_user_carts(request)
    
    stop_violations = check_cart_for_stop_list(carts, terminal_id)
    if stop_violations:
        items_str = ", ".join(stop_violations)
        return JsonResponse({
            'status': 'error', 
            'message': f'На жаль, ці товари щойно закінчилися: {items_str}. Будь ласка, видаліть їх з кошика.'
        })

    return JsonResponse({
        "status": "success",
        "terminal_id": request.session['terminal_id'],
        "delivery_cost": request.session.get('delivery_cost', 0)
    })


def get_user_cart_or_404(request, cart_id):
    """
    Повертає cart item тільки з поточної сесії.
    Якщо item не належить цій сесії — 404.
    """
    return get_object_or_404(get_user_carts(request), id=cart_id)


def render_cart_html(request):
    carts = get_user_carts(request)
    totals = get_cart_totals(request)

    context = {
        "carts": carts,
        **totals,
    }

    template = "carts/includes/cart_items.html" if carts.exists() else "carts/includes/empty_included_cart.html"
    return render_to_string(template, context, request=request)


def cart_add(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)

    try:
        qty_to_add = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        qty_to_add = 1


    selected_terminal = request.session.get('terminal_id')
    order_type = request.session.get('order_type')

    # КРОК 1: Перевірка наявності типу замовлення
    if not order_type or (order_type == 'PICKUP' and not selected_terminal):
        restaurants = Restaurant.objects.all()
        restaurants_data = [
            {
                'id': str(r.id),
                'name': str(r.name_uk or r.name),
                'address': str(r.address_uk or r.address)
            } for r in restaurants
        ]
        return JsonResponse({"status": "select_type_required", "all_restaurants": restaurants_data})

    # КРОК 2: Пошук стоп-листа (РЕФАКТОРИНГ ОПТИМІЗАЦІЇ)
    stop_product_ids = set()
    if selected_terminal:
        # ДОДАНО КЕШУВАННЯ: перевіряємо, чи є стоп-лист у кеші на 2 хвилини
        cache_key = f"stop_list_{selected_terminal}"
        stop_product_ids = cache.get(cache_key)

        if stop_product_ids is None:
            stop_product_ids = set()
            client = SyrveClient()
            raw_data = client.get_stop_lists()
            
            stop_lists = raw_data.get("terminalGroupStopLists", [])
            for org in stop_lists:
                terminals = org.get("items", [])
                for tg in terminals:
                    t_id = str(tg.get("terminalGroupId", "")).lower()
                    if t_id == str(selected_terminal).lower():
                        items = tg.get("items", [])
                        for item in items:
                            p_id = item.get("productId")
                            if p_id:
                                stop_product_ids.add(str(p_id).lower())
            
            # Зберігаємо в кеш на 120 секунд
            cache.set(cache_key, stop_product_ids, 120)

    # ПЕРЕВІРКА СТОПА
    product_uuid = str(product.id).lower()
    if product_uuid in stop_product_ids:
        return JsonResponse({
            "status": "error", 
            "message": f"Вибачте, '{product.name}' закінчився за цією адресою."
        }, status=400)

    # КРОК 3: Додавання в кошик
    if not request.session.session_key:
        request.session.create()
    
    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key, 
        product=product,
        defaults={'quantity': 0} 
    )
    cart.quantity += qty_to_add
    cart.save()
    

    user_carts = get_user_carts(request)
    aggr = user_carts.aggregate(total=Sum('quantity'))
    total_q = aggr['total'] or 0

    if order_type == 'DELIVERY':
        delivery_cost = calculate_delivery_cost(user_carts.total_prace())
        request.session['delivery_cost'] = 0 if delivery_cost is None else delivery_cost
        request.session.modified = True

    return JsonResponse({
        "status": "success",
        "cart_count": total_q,
        'cart_html': render_cart_html(request),
    })



def get_cart_totals(request):
    """Допоміжна функція для отримання всіх сум кошика"""
    user_carts = get_user_carts(request)
    cart_total = user_carts.total_prace()
    
    delivery_cost = 0
    order_type = request.session.get('order_type')
    
    if order_type == 'DELIVERY':
        calc_delivery = calculate_delivery_cost(cart_total)
        delivery_cost = 0 if calc_delivery is None else calc_delivery
            
        request.session['delivery_cost'] = delivery_cost
        request.session.modified = True

    return {
        'cart_total_price': cart_total,
        'delivery_cost': delivery_cost,
        'full_total_sum': cart_total + delivery_cost,
        'cart_count': user_carts.aggregate(total=Sum('quantity'))['total'] or 0,
        'can_checkout': (order_type != 'DELIVERY') or (cart_total >= 2000),
        'delivery_min_missing': max(0, 2000 - cart_total) if order_type == 'DELIVERY' else 0,
    }

@require_POST
def cart_change(request, cart_id):
    cart = get_user_cart_or_404(request, cart_id)
    action = request.POST.get('action')
    
    if action == 'plus':
        cart.quantity += 1
        cart.save()
    elif action == 'minus':
        if cart.quantity > 1:
            cart.quantity -= 1
            cart.save()
        else:
            cart.delete()
            return JsonResponse({'status': 'deleted', 'cart_id': cart_id, **get_cart_totals(request)})

    return JsonResponse({
        'status': 'success',
        'cart_id': cart.id,
        'quantity': cart.quantity,
        'item_total': cart.product_prace(),
        'cart_html': render_cart_html(request),
        **get_cart_totals(request)
    })

@require_POST
def cart_remove(request, cart_id):
    cart = get_user_cart_or_404(request, cart_id)
    cart.delete()
    

    totals = get_cart_totals(request)
    
    return JsonResponse({
        'status': 'success',
        'item_id': cart_id, 
        'cart_html': render_cart_html(request),
        **totals
    })



def cart_count(request):
    qs = get_user_carts(request)
    
    total_quantity = qs.aggregate(total=Sum('quantity'))['total'] or 0

    return JsonResponse({
        'count': total_quantity, 
        'items': list(qs.values_list('product__slug', flat=True))
        
    })

