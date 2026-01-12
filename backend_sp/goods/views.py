from django.shortcuts import render, get_object_or_404
import requests
from django.http import JsonResponse
from django.db.models.functions import Lower
from goods.models import Product, Group, GroupModifier, GroupModifierChild
from django.db.models import Q

from django.utils.translation import get_language
from carts.utils import get_user_carts


def catalog(request):
    products = Product.objects.filter(is_included_in_menu=True)
    groups = Group.objects.filter(is_included_in_menu=True, parent__isnull=True).order_by('order')
    context = {
        'products': products,
        'groups': groups,  # для меню
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



def create_order_telegram(request):
    if request.method == 'POST':
  
        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        location_key = request.POST.get('location', '').strip()
        

        current_lang = get_language().upper()


        carts = get_user_carts(request)
        if not carts.exists():
            return JsonResponse({'status': 'error', 'message': 'Кошик порожній'})


        topics = {
            "skymall": 2,      
            "retroville": 4,   
        }

        location_names = {
            "skymall": "ТРЦ SkyMall",
            "retroville": "ТРЦ Retroville"
        }

        target_topic = topics.get(location_key)
        display_location = location_names.get(location_key, "Не вказано")


        items_text = ""
        total_price = 0
        for item in carts:
            sum_item = item.product.price * item.quantity

            items_text += f"• {item.product.name} — <b>{item.quantity} шт.</b> ({sum_item} грн)\n"
            total_price += sum_item

        message = (
            f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ З САЙТУ({current_lang})</b>\n\n"
            f"👤 <b>Клієнт:</b> {name} {surname}\n"
            f"📞 <b>Телефон:</b> {phone}\n"
            f"📧 <b>Email:</b> {email}\n"
            f"📦 <b>Товари:</b>\n{items_text}\n"    
            f"💰 <b>РАЗОМ: {total_price} грн</b>"
        )


        TOKEN = "7957796004:AAEc8529j0JBejt8oR60v3CptvrDlO1CXtg"
        CHAT_ID = "-1003599444381"

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "message_thread_id": target_topic
        }

        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
 
                carts.delete()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Telegram API error: {response.status_code}'
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


