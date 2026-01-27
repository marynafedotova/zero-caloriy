import re
from users.models import User, Address


def get_or_create_customer_with_address(name, phone, order_type, address_data=None):

    
    # 1. Створюємо або оновлюємо користувача
    # Очищаємо телефон для BigInt ID
    clean_id = re.sub(r'\D', '', phone)
    user_id = int(clean_id[-15:]) if clean_id else 0

    user, created = User.objects.update_or_create(
        user_id=user_id,
        defaults={
            'first_name': name,
            'phone': phone,
        }
    )

    # 2. Якщо це доставка — створюємо адресу
    address_obj = None
    if order_type == 'DELIVERY' and address_data:
        address_obj = Address.objects.create(
            user=user,
            street=address_data.get('street', ''),
            house_number=address_data.get('house_number', ''),
            apartment_number=address_data.get('apartment_number', ''),
            entrance=address_data.get('entrance', ''),
            floor=address_data.get('floor', '')
        )
    
    return user, address_obj