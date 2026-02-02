import os
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
            "modifiers": [] 
        })

    external_id = uuid.uuid4() 

    payload = {
        "organizationId": os.getenv("ORG_ID"),
        "terminalGroupId": str(order.terminal_group_id),
        "order": {
            "id": str(external_id),
            "externalNumber": f"WEB-{order.id}",
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
                "checkStopList": True 
            },
            "payments": [
                {
                    "paymentTypeKind": "CASH",
                    "sum": float(order.total_amount),
                    "paymentTypeId": "09322f46-578a-d210-add7-eec222a08871" 
                }
            ]
        }
    }


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