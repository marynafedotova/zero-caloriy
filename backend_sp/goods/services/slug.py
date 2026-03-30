import os
import django
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_sp.settings')
django.setup()

# Тепер можна імпортувати моделі та використовувати базу
from goods.models import Product

#import translitcodec # Якщо назви кирилицею
from django.utils.text import slugify

def generate_smart_slug(name_en, weight):
    # 1. Очищуємо назву від "баночка", "сфера" тощо
    # Припустимо, ми відсікаємо останнє слово
    name_parts = name_en.split(' ')
    if len(name_parts) > 1:
        base_name = " ".join(name_parts[:-1])
    else:
        base_name = name_parts[0]
    
    # 2. Переводимо вагу в грами (наприклад, 0.23 -> 230)
    weight_in_grams = int(weight * 1000)
    
    # 3. Формуємо фінальний слаг
    # Наприклад: "napoleon-230"
    full_slug = f"{slugify(base_name)}-{weight_in_grams}"
    
    return full_slug


def force_update_all_slugs():
    all_products = Product.objects.filter(is_visible=True)
    count = all_products.count()
 

    updated_count = 0
    for product in all_products:
        # Зберігаємо старий слаг для виводу (якщо він був)
        old_slug = product.slug if product.slug else "ПЕРЕПУСТКА"
        
        # Генеруємо новий слаг за нашою функцією
        new_slug = generate_smart_slug(product.name_en, product.weight)
        
        # Перезаписуємо
        product.slug = new_slug
        product.save()
        
        updated_count += 1
        # Виводимо результат перетворення
        print(f"✅ {product.name_en}: [{old_slug}] ➔ [{new_slug}]")

    print(f"\n✨ Готово! Оновлено товарів: {updated_count}")

if __name__ == "__main__":
    force_update_all_slugs()