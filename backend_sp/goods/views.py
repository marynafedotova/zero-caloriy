import os
import requests
import re

from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils.translation import get_language

from goods.models import Product, Group, GroupModifier, GroupModifierChild
from carts.utils import get_user_carts
from orders.models import Order, OrderItem
from goods.services.syrve_client import SyrveClient
from orders.services import build_syrve_payload
from users.views import get_or_create_customer_with_address




def catalog(request):

    selected_categories = request.GET.getlist('category')
    
    products = Product.objects.filter(is_included_in_menu=True)
    groups = Group.objects.filter(is_included_in_menu=True, parent__isnull=True).order_by('order')

    if selected_categories:
        products = products.filter(categories__slug__in=selected_categories).distinct()

    context = {
        'products': products,
        'groups': groups,
        'selected_categories': selected_categories, 
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

    
    random_products = Product.objects.exclude(id=product.id).order_by('?')[:5]

    context = {
        "product": product,
        "child_modifiers": modifiers_data,
        "variants": product_variants,
        "random_products": random_products,
    }
    return render(request, "goods/product.html", context)


# def product(request, product_slug, group_slug=None):

#     product = get_object_or_404(Product, slug=product_slug)


#     name_parts = product.name_uk.split(' ')
    

#     if len(name_parts) > 1:
#         base_name = " ".join(name_parts[:-1])
#     else:
#         base_name = name_parts[0]


#     product_variants = Product.objects.filter(
#         name_uk__istartswith=base_name,
#         size__isnull=False 
#     ).select_related('size').order_by('weight')


#     if not product_variants.exists():
#         product_variants = [product]


#     group_modifiers = GroupModifier.objects.filter(product=product).prefetch_related(
#         'groupmodifierchild_set__modifier'
#     )

#     modifiers_data = []
#     for gm in group_modifiers:
#         modifiers_data.append({
#             "group_modifier": gm,
#             "child_modifiers": [child.modifier for child in gm.groupmodifierchild_set.all()],
#         })


#     random_products = Product.objects.exclude(id=product.id).order_by('?')[:5]

#     context = {
#         "product": product,
#         "child_modifiers": modifiers_data,
#         "variants": product_variants,
#         "random_products": random_products,
#     }
    
#     return render(request, "goods/product.html", context)


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
        ).filter(search_filter).distinct()
    else:
        products = Product.objects.none()

    context = {
        'goods': products, 
        'query': query,
    }

    return render(request, 'goods/search_results.html', context)



@transaction.atomic
def create_order_telegram(request):
    if request.method == 'POST':
        # --- 1. ОДЕРЖАННЯ ДАНИХ ---
        order_type = request.session.get('order_type') # 'PICKUP' або 'DELIVERY'
        order_type_id = request.session.get('order_type_id')
        terminal_id = request.session.get('terminal_id')
        
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        comment = request.POST.get('comment', '').strip()
        delivery_time = request.POST.get('delivery_time', '').strip()

        carts = get_user_carts(request)
        if not carts.exists():
            return JsonResponse({'status': 'error', 'message': 'Кошик порожній'})

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
        order = Order.objects.create(
            user=user_obj,
            order_type_id=order_type_id,
            terminal_group_id=terminal_id,
            address=address_obj,
            total_amount=carts.total_prace(),
            comment=f"{comment} | Час: {delivery_time}".strip(),
            status='NEW'
        )

        # Створюємо товари
        for item in carts:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price # або item.product_prace
            )

        # --- 4. ВІДПРАВКА В SYRVE ---
        syrve_info = "Не відправлено"
        client = SyrveClient()
        try:
            payload = build_syrve_payload(order, carts)
            syrve_res, status_code = client.create_order(payload)
            if status_code in [200, 201]:
                order.syrve_id = syrve_res.get('correlationId')
                order.status = 'SENT'
                order.save()
                syrve_info = "✅ ПРИЙНЯТО SYRVE"
            else:
                syrve_info = f"❌ ПОМИЛКА SYRVE: {syrve_res.get('errorDescription', 'Err')}"
        except Exception as e:
            syrve_info = f"⚠️ ПОМИЛКА API: {str(e)}"

        # --- 5. ФОРМУВАННЯ ПОВІДОМЛЕННЯ ДЛЯ TELEGRAM ---
        items_text = "".join([f"• {item.product.name} — <b>{item.quantity} шт.</b>\n" for item in carts])
        common_footer = (
            f"📦 <b>Товари:</b>\n{items_text}\n"
            f"💰 <b>РАЗОМ: {order.total_amount} грн</b>\n"
            f"💬 <b>Комент:</b> {comment}"
        )

        if order_type == 'PICKUP':
            location_name = "ТРЦ SkyMall" if str(terminal_id) == os.getenv("TERMINAL_SKY_MALL") else "ТРЦ Retroville"
            message = (
                f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ — САМОВИВІЗ ({syrve_info})</b>\n\n"
                f"👤 <b>Клієнт:</b> {name}\n"
                f"📞 <b>Телефон:</b> {phone}\n"
                f"🏪 <b>Точка видачі:</b> {location_name}\n"
                f"🕒 <b>Забере о:</b> {delivery_time}\n\n"
                f"{common_footer}"
            )
        else:
            # Тут беремо дані з address_fields, бо в order.street цих полів немає
            message = (
                f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ — ДОСТАВКА ({syrve_info})</b>\n\n"
                f"👤 <b>Клієнт:</b> {name}\n"
                f"📞 <b>Телефон:</b> {phone}\n"
                f"📍 <b>Адреса:</b> вул. {address_fields['street']}, буд. {address_fields['house_number']}\n"
                f"🏢 <b>Деталі:</b> кв. {address_fields['apartment_number']}, під'їзд {address_fields['entrance']}, поверх {address_fields['floor']}\n"
                f"🕒 <b>Бажаний час:</b> {delivery_time}\n\n"
                f"{common_footer}"
            )

        # --- 6. ВІДПРАВКА В TELEGRAM ТА ОЧИЩЕННЯ ---
        topics = {
            os.getenv("TERMINAL_SKY_MALL"): 2,
            os.getenv("TERMINAL_RETROVILLE"): 4,
        }
        target_topic = topics.get(str(terminal_id), 2)

        try:
            tg_res = requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", data={
                "chat_id": os.getenv('CHAT_ID'),
                "text": message,
                "parse_mode": "HTML",
                "message_thread_id": target_topic
            })
            
            if tg_res.status_code == 200:
                carts.delete() 
                request.session.pop('order_type', None) 
                request.session.pop('order_type_id', None)
                request.session.pop('terminal_id', None)
                return JsonResponse({'status': 'success'})
        except:
            pass 

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



# def create_order_telegram(request):
#     if request.method == 'POST':
  
#         name = request.POST.get('name', '').strip()
#         surname = request.POST.get('surname', '').strip()
#         phone = request.POST.get('phone', '').strip()
#         email = request.POST.get('email', '').strip()
#         location_key = request.POST.get('location', '').strip()
        

#         current_lang = get_language().upper()


#         carts = get_user_carts(request)
#         if not carts.exists():
#             return JsonResponse({'status': 'error', 'message': 'Кошик порожній'})


#         topics = {
#             "skymall": 2,      
#             "retroville": 4,   
#         }

#         location_names = {
#             "skymall": "ТРЦ SkyMall",
#             "retroville": "ТРЦ Retroville"
#         }

#         target_topic = topics.get(location_key)
#         display_location = location_names.get(location_key, "Не вказано")


#         items_text = ""
#         total_price = 0
#         for item in carts:
#             sum_item = item.product.price * item.quantity

#             items_text += f"• {item.product.name} — <b>{item.quantity} шт.</b> ({sum_item} грн)\n"
#             total_price += sum_item

#         message = (
#             f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ З САЙТУ({current_lang})</b>\n\n"
#             f"👤 <b>Клієнт:</b> {name} {surname}\n"
#             f"📞 <b>Телефон:</b> {phone}\n"
#             f"📧 <b>Email:</b> {email}\n"
#             f"📦 <b>Товари:</b>\n{items_text}\n"    
#             f"💰 <b>РАЗОМ: {total_price} грн</b>"
#         )


#         TOKEN = os.getenv('TOKEN')
#         CHAT_ID = os.getenv('CHAT_ID')

#         url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
#         payload = {
#             "chat_id": CHAT_ID,
#             "text": message,
#             "parse_mode": "HTML",
#             "message_thread_id": target_topic
#         }

#         try:
#             response = requests.post(url, data=payload)
#             if response.status_code == 200:
 
#                 carts.delete()
#                 return JsonResponse({'status': 'success'})
#             else:
#                 return JsonResponse({
#                     'status': 'error', 
#                     'message': f'Telegram API error: {response.status_code}'
#                 })
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})

#     return JsonResponse({'status': 'error', 'message': 'Invalid request'})


