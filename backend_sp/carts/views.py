import os
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from goods.models import Product, Restaurant
from carts.models import Cart
from carts.utils import get_user_carts
from goods.services.syrve_client import SyrveClient



def set_order_type(request):
    if request.method == 'POST':
        order_type_key = request.POST.get('type')  
        terminal_id = request.POST.get('terminal_id')

        
        MAPPING = {
            'DELIVERY': '49cf98d2-25ab-d404-a5a8-11eaffc7ce7f', 
            'PICKUP': '7bb5d30f-c8bc-d694-93a8-0d955e274921',   
        }

        # Зберігаємо в сесію саме UUID для Syrve
        selected_syrve_id = MAPPING.get(order_type_key)
        
        if not selected_syrve_id:
            return JsonResponse({"status": "error", "message": "Невідомий тип замовлення"}, status=400)

        user_carts = get_user_carts(request)
        total_price = user_carts.total_prace()

        if order_type_key == 'DELIVERY':
            if total_price < 2000:
                return JsonResponse({
                    "status": "error",
                    "error_type": "low_sum",
                    "message": f"Доставка таксі від 2000 грн. Зараз: {total_price} грн."
                }, status=400)
            
            # Логіка терміналів для доставки
            if total_price >= 4000:
                request.session['terminal_id'] = "427d6dd2-1d65-275f-014c-ec534e53008e"
            else:
                request.session['terminal_id'] = os.getenv("TERMINAL_GROUP_ID")

        if order_type_key == 'PICKUP' and terminal_id:
            request.session['terminal_id'] = terminal_id

        # Зберігаємо все в сесію
        request.session['order_type_key'] = order_type_key # Для фронта ('DELIVERY')
        request.session['order_type_id'] = selected_syrve_id # Для Syrve (UUID)
        request.session.modified = True
        
        return JsonResponse({"status": "success"})
    

    

def cart_add(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    selected_terminal = request.session.get('terminal_id')
    order_type = request.session.get('order_type')

    # ШАГ 1: Перевірка наявності типу замовлення
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


    # ШАГ 2: Пошук стоп-листа
    # Усередині вашого views.py -> cart_add
    stop_product_ids = set()
    if selected_terminal:
        client = SyrveClient()
        raw_data = client.get_stop_lists()  # Тепер тут повний словник
        
        # Починаємо занурення згідно з вашим JSON
        stop_lists = raw_data.get("terminalGroupStopLists", [])
        
        for org in stop_lists:
            # В кожній організації є items (це список терміналів)
            terminals = org.get("items", [])
            for tg in terminals:
                t_id = str(tg.get("terminalGroupId", "")).lower()
                
                # Порівнюємо термінал з обраним у сесії
                if t_id == str(selected_terminal).lower():
                    # Ми знайшли потрібний ресторан, беремо його товари
                    items = tg.get("items", [])
                    for item in items:
                        p_id = item.get("productId")
                        if p_id:
                            stop_product_ids.add(str(p_id).lower())

    print(f"DEBUG: Кількість стопів для терміналу {selected_terminal}: {len(stop_product_ids)}")
            


    # ПЕРЕВІРКА
    product_uuid = str(product.id).lower()
    if product_uuid in stop_product_ids:
        print(f"БЛОКУЄМО ТОВАР: {product.name}")
        return JsonResponse({
            "status": "error", 
            "message": f"Вибачте, '{product.name}' закінчився за цією адресою."
        }, status=400)

    # ШАГ 3: Додавання в кошик (якщо не в стопі)
    if not request.session.session_key:
        request.session.create()
    
    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key, 
        product=product,
        defaults={'quantity': 0} 
    )
    cart.quantity += 1
    cart.save()
    return JsonResponse({"status": "success"})


def cart_change(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id)
    
    if request.method == 'POST':
        action = request.POST.get('action') 
        quantity = request.POST.get('quantity') 

        if action == 'plus':
            cart.quantity += 1
        elif action == 'minus':
            if cart.quantity > 1:
                cart.quantity -= 1
            else:
                cart.delete()
                return redirect(request.META.get('HTTP_REFERER', '/'))
        elif quantity and quantity.isdigit():
            cart.quantity = int(quantity)
        
        cart.save()
        messages.success(request, f"Кількість товару {cart.product.name} змінено.")
    
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else '/')


def cart_remove(request, cart_id):

    cart = Cart.objects.get(id=cart_id)
    cart.delete()

    referer = request.META.get('HTTP_REFERER')
    
    return redirect(referer if referer else '/')




def cart_count(request):
    if not request.session.session_key:
        return JsonResponse({'count': 0})

    count = Cart.objects.filter(
        session_key=request.session.session_key
    ).count()

    return JsonResponse({'count': count})


