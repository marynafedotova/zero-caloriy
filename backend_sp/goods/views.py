import os
import requests
import re
import logging
from django.core.cache import cache
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils.translation import get_language

from goods.models import Product, Group, GroupModifier, GroupModifierChild, Restaurant
from carts.utils import get_user_carts, calculate_delivery_cost
from orders.models import Order, OrderItem
from goods.services.syrve_client import SyrveClient
from orders.services.services import build_syrve_payload, finish_order_process, create_monobank_invoice
from users.views import get_or_create_customer_with_address
from django.core.paginator import Paginator
from django.template.loader import render_to_string

from django.core.paginator import Paginator

def catalog(request):
    selected_categories = request.GET.getlist('category')

    products = Product.objects.filter(is_visible=True)
    groups = Group.objects.filter(is_included_in_menu=True, parent__isnull=True).order_by('order')

    if selected_categories:
        products = products.filter(categories__slug__in=selected_categories).distinct()

    products = products.order_by('-id') 

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        paginator = Paginator(products, 4) 
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        html = render_to_string(
            "goods/product_items.html",
            {"products": page_obj},
            request=request
        )

        return JsonResponse({
            "html": html,
            "has_next": page_obj.has_next()
        })

    context = {
        "products": products,
        "groups": groups,
        "selected_categories": selected_categories,
    }
    return render(request, "goods/catalog.html", context)


def product(request, product_slug, group_slug=None):
    # Отримуємо основний продукт один раз
    product = get_object_or_404(Product, slug=product_slug)
    
    #отримання модифікаторів (використовуємо prefetch_related)
    group_modifiers = GroupModifier.objects.filter(product=product).prefetch_related(
        'groupmodifierchild_set__modifier'
    )

    modifiers_data = []
    for gm in group_modifiers:
        modifiers_data.append({
            "group_modifier": gm,
            "child_modifiers": [child.modifier for child in gm.groupmodifierchild_set.all()],
        })

    # Пошук варіантів (вага/розмір)
    first_word = product.name_uk.split(' ')[0]
    product_variants = Product.objects.filter(
        name_uk__icontains=first_word,
        size__isnull=False 
    ).select_related('size').order_by('weight')

    if not product_variants.exists():
        product_variants = [product]

    
    random_products = Product.objects.filter(is_visible=True).exclude(id=product.id).order_by('?')[:5]

    context = {
        "product": product,
        "child_modifiers": modifiers_data,
        "variants": product_variants,
        "random_products": random_products,
    }
    return render(request, "goods/product.html", context)


def cart(request):
    return render(request, "goods/cart.html")



def product_search(request):
    query = request.GET.get('q', '').strip()
    
    if query:
       
        query_lower = query.lower()
        words = query_lower.split()
        
        search_filter = Q()

        for word in words:
        
            words_filter = (
                Q(name_uk_lower__contains=word) | 
                Q(name_en_lower__contains=word) |
                Q(name_ru_lower__contains=word) |
                Q(additional_info_uk_lower__contains=word) |
                Q(additional_info_en_lower__contains=word) |
                Q(additional_info_ru_lower__contains=word) |
                Q(about_product_uk_lower__contains=word) |
                Q(about_product_en_lower__contains=word) |
                Q(about_product_ru_lower__contains=word) |
                Q(description_uk_lower__contains=word) | 
                Q(description_en_lower__contains=word) |
                Q(description_ru_lower__contains=word)     
            )
            search_filter &= words_filter

       
        products = Product.objects.annotate(
            name_uk_lower=Lower('name_uk'),
            name_en_lower=Lower('name_en'),
            name_ru_lower=Lower('name_ru'),
            description_uk_lower=Lower('description_uk'),
            description_en_lower=Lower('description_en'),
            description_ru_lower=Lower('description_ru'),
            additional_info_uk_lower=Lower('additional_info_uk'),
            additional_info_en_lower=Lower('additional_info_en'),
            additional_info_ru_lower=Lower('additional_info_ru'),
            about_product_uk_lower=Lower('about_product_uk'),
            about_product_en_lower=Lower('about_product_en'),
            about_product_ru_lower=Lower('about_product_ru'),
        ).filter(search_filter, is_visible=True).distinct()
    else:
        products = Product.objects.none()

    context = {
        'goods': products, 
        'query': query,
    }

    return render(request, 'goods/search_results.html', context)


def check_cart_for_stop_list(carts, terminal_id):
    """
    Повертає список назв товарів, які зараз у стоп-листі для вказаного терміналу.
    Якщо список порожній — все добре.
    """
    if not terminal_id or not carts.exists():
        return []

    cache_key = f"stop_list_{terminal_id}"
    stop_product_ids = cache.get(cache_key)

    if stop_product_ids is None:
        stop_product_ids = set()
        try:
            client = SyrveClient()
            raw_data = client.get_stop_lists()
            stop_lists = raw_data.get("terminalGroupStopLists", [])
            for org in stop_lists:
                for tg in org.get("items", []):
                    if str(tg.get("terminalGroupId", "")).lower() == str(terminal_id).lower():
                        for item in tg.get("items", []):
                            p_id = item.get("productId")
                            if p_id:
                                stop_product_ids.add(str(p_id).lower())
            cache.set(cache_key, stop_product_ids, 120)
        except Exception as e:
            print(f"Stop list fetch error: {e}")
            return []

    forbidden_items = [
        item.product.name 
        for item in carts 
        if str(item.product.id).lower() in stop_product_ids
    ]
    
    return forbidden_items

logger = logging.getLogger(__name__)

@transaction.atomic
def create_order_telegram(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': '{% ftlmsg "іnvalid_method" %}'})
        # --- 1. ОДЕРЖАННЯ ДАНИХ ---
    order_type = request.session.get('order_type')         
    order_type_id = request.session.get('order_type_id')
    terminal_id = request.session.get('terminal_id')
    payment_type = request.POST.get('payment_type')   
    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    comment = request.POST.get('comment', '').strip()
    delivery_time = request.POST.get('delivery_time', '').strip()

    carts = get_user_carts(request)

    if not carts.exists():
        return JsonResponse({'status': 'error', 'message': '{% ftlmsg "cart_empty" %}'})

    total_price = carts.total_prace()

    delivery_price = calculate_delivery_cost(total_price)
    if order_type == 'DELIVERY' and delivery_price is None:
        return JsonResponse({
            'status': 'error', 
            'message': '{% ftlmsg "min_sum_dlvr" %}'
        }) 
        
    MAIN_DELIVERY_TERMINAL = os.getenv("TERMINAL_SKY_MALL")
    if order_type == 'DELIVERY' and total_price >= 2000:
        terminal_id = MAIN_DELIVERY_TERMINAL

    restaurant_obj_id = Restaurant.objects.filter(id=terminal_id).first()

    stop_violations = check_cart_for_stop_list(carts, restaurant_obj_id)
    if stop_violations:
        items_str = ", ".join(stop_violations)
        return JsonResponse({
            'status': 'error', 
            'message': f'На жаль, ці товари щойно закінчилися: {items_str}. Будь ласка, видаліть їх з кошика.'
        })

    # --- 2. СТВОРЕННЯ КОРИСТУВАЧА ТА АДРЕСИ ---
    address_fields = {
        'street': request.POST.get('street', ''),
        'house_number': request.POST.get('house_number', ''),
        'apartment_number': request.POST.get('apartment_number', ''),
        'entrance': request.POST.get('entrance', ''),
        'floor': request.POST.get('floor', ''),
    }
        
    user_obj, address_obj = get_or_create_customer_with_address(
        name, phone, order_type, address_fields
    )


    

    # --- 3. СТВОРЕННЯ ЗАМОВЛЕННЯ ---
    final_total = total_price + (200 if (order_type == 'DELIVERY' and delivery_price == 200) else 0)
    

    order = Order.objects.create(
        source='WEB',
        user=user_obj,
        order_type_id=order_type_id,
        terminal_group_id=restaurant_obj_id,
        address=address_obj,
        total_amount=final_total,
        comment=f"{comment} | Час: {delivery_time}".strip(),
        status='PENDING' if payment_type == 'paid' else 'COD', 
        
    )

    # Створюємо товари
    for item in carts:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price 
        )

    if order_type == 'DELIVERY' and delivery_price == 200:
        delivery_product = Product.objects.get(id="3d496ec8-0993-4eeb-acf0-3216148d416f")
        OrderItem.objects.create(
            order=order,
            product=delivery_product,
            quantity=1,
            price=delivery_product.price
        )

        # db_items = order.items.all()
        # order_number = f"WEB-{order.id}"

    print(payment_type)
    # --- ЛОГІКА ОПЛАТИ ---
    if payment_type == 'paid':
        mono_res = create_monobank_invoice(order)
        if mono_res.status_code == 200:
            data = mono_res.json()
            order.monobank_invoice_id = data['invoiceId']
            order.save()

            return JsonResponse({
                'status': 'pay', 
                'pay_url': data['pageUrl']
            })
        else:
            logger.error(f"Mono error: {mono_res.text}")
            return JsonResponse({'status': 'error', 'message': '{% ftlmsg "error_plat_sys" %}'})


    else:
        print("я увійшов в умови оплата при отриманні")

        order.comment = f"⚠️ ОПЛАТА ПРИ ОТРИМАННІ | {order.comment}"
        print("я уту")
        order.save()

        print("DEBUG: Calling finish_order_process for COD order")

        finish_order_process(order)
        return JsonResponse({'status': 'success', 'order_number': f"{order.source}-{order.id}"})

 