import uuid
from django.conf import settings

def build_syrve_payload(order, cart_items):
    """
    Формує JSON для /api/1/deliveries/create
    """
    items = []
    for item in cart_items:
        items.append({
            "type": "Product",
            "productId": str(item.product.id),
            "amount": float(item.quantity),
            "modifiers": [] # Якщо додасте модифікатори в Cart, сюди піде масив
        })

    # Створюємо унікальний ID для замовлення (щоб уникнути дублів)
    # Якщо замовлення не пройде, можна буде відправити з цим же ID повторно
    external_id = uuid.uuid4() 

    payload = {
        "organizationId": settings.SYRVE_ORG_ID,
        "terminalGroupId": str(order.terminal_group_id),
        "order": {
            "id": str(external_id),
            "externalNumber": f"WEB-{order.id}", # Номер замовлення для касирів
            "items": items,
            "phone": str(order.user.phone),
            "orderTypeId": str(order.order_type_id),
            "comment": order.comment or "Замовлення з сайту",
            "customer": {
                "name": order.user.first_name or "Клієнт"
            },
            "createOrderSettings": {
                "servicePrint": True,
                "transportToFrontTimeout": 0,
                "checkStopList": True # Краще увімкнути, щоб iiko перевірила стопи ще раз
            },
            "payments": [
                {
                    "paymentTypeKind": "CASH", # Або CARD
                    "sum": float(order.total_amount),
                    "paymentTypeId": "09322f46-578a-d210-add7-eec222a08871" # Твій ID готівки
                }
            ]
        }
    }

    # Логіка адреси (для PICKUP deliveryPoint не потрібен)
    if order.address:
        payload["order"]["deliveryPoint"] = {
            "address": {
                "street": {
                    "name": order.address.street,
                    "city": order.address.city or "Київ"
                },
                "house": str(order.address.house_number),
                "flat": str(order.address.apartment_number or ""),
                "entrance": str(order.address.entrance or ""),
                "floor": str(order.address.floor or ""),
                "doorphone": ""
            }
        }
    
    return payload