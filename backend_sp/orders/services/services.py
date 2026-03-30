import os
import uuid
import requests
import logging
import base64
import hashlib
from django.conf import settings
from orders.models import Order
from goods.services.syrve_client import SyrveClient

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key


logger = logging.getLogger(__name__)

def finish_order_process(order):
    """Головна функція завершення: Syrve + Telegram"""
    print(f"--- START FINISH PROCESS FOR ORDER {order.id} ---", flush=True)
    term_id = str(order.terminal_group_id.id)
    db_items = order.items.all()
    print(f"Items count: {db_items.count()}")
    
    # 1. Відправка в Syrve
    syrve_ok, syrve_info = send_order_to_syrve(order, db_items)
    print(f"Syrve status: {syrve_ok}, Info: {syrve_info}")
    # 2. Підготовка даних для Telegram (конфіг локацій)

    print(f"Looking for terminal ID: {term_id}")
    LOCATIONS_CONFIG = {
        os.getenv("TERMINAL_SKY_MALL"): {"name": "ТРЦ SkyMall", "topic": 2, "admin_tag": "@zerokaloriySkymall"},
        os.getenv("TERMINAL_RETROVILLE"): {"name": "ТРЦ Retroville", "topic": 4, "admin_tag": "@zerokaloriyRetroville"},
        os.getenv("TERMINAL_RAJON"): {"name": "ТРЦ РайON", "topic": 1887, "admin_tag": "@zerokaloriyRayon"},
        os.getenv("TERMINAL_TEST"): {"name": "ТРЦ Тест", "topic": 8765478, "admin_tag": "@zerokaloriy"}
    }
    loc_data = LOCATIONS_CONFIG.get(term_id, {"name": "Локація", "topic": 1, "admin_tag": ""})
    print(f"Location found: {loc_data['name']}")
    # 3. Відправка в Telegram
    
    send_order_to_telegram(order, db_items, loc_data, syrve_info)
    
    return True


def send_order_to_syrve(order, db_items):
    client = SyrveClient()
    try:
        payload = build_syrve_payload(order, db_items)
        response, status_code = client.create_order(payload)
        if status_code in [200, 201]:
            order.syrve_id = response.get("correlationId")
            if order.status != "PAID": order.status = "COD"
            order.save()
            return True, "✅ ПРИЙНЯТО SYRVE"
        return False, f"❌ ПОМИЛКА SYRVE ({status_code}- {response})"

    except Exception as e:
        print(f"!!! SYRVE CRITICAL ERROR: {str(e)}")
        return False, f"⚠️ API ERROR: {str(e)}"



def build_syrve_payload(order, cart_items):
    """
    Формує JSON для /api/1/deliveries/create з урахуванням статусу оплати.
    """
    terminal_id = str(order.terminal_group_id.id)
    items = []
    for item in cart_items:
        items.append({
            "type": "Product",
            "productId": str(item.product.id),
            "amount": float(item.quantity),
            "modifiers": [] 
        })

    # --- ЛОГІКА КОМЕНТАРЯ ТА ОПЛАТИ ---
    payments = []

    if order.status == 'PAID':
        # Якщо оплачено через Monobank — передаємо дані про оплату
        MONO_PAYMENT_TYPE_ID = os.getenv("MONO_PAYMENT_TYPE")
        
        payments.append({
            "paymentTypeKind": "Card",
            "sum": float(order.total_amount),
            "paymentTypeId": MONO_PAYMENT_TYPE_ID,
            "isProcessedExternally": True  # Позначаємо, що гроші вже отримані
        })
        final_comment = order.comment
    else:
        # Якщо оплати ще немає (самовивіз/готівка) — додаємо мітку в коментар
        # Блок payments залишаємо порожнім
        final_comment = order.comment

    payload = {
        "organizationId": os.getenv("ORG_ID"),
        "terminalGroupId": terminal_id,
        "order": {
            "id": str(uuid.uuid4()),
            "externalNumber": f"{order.source}-{order.id}",
            "items": items,
            "phone": str(order.user.phone),
            "orderTypeId": str(order.order_type_id),
            "comment": final_comment,
            "customer": {
                "name": order.user.first_name or "Клієнт"
            },
            "createOrderSettings": {
                "servicePrint": True,
                "checkStopList": True 
            }
        }
    }

    # Додаємо адресу, якщо вона є
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


def send_order_to_telegram(order, db_items, loc_data, syrve_info):
    items_text = "".join([f"• {i.product.name} — <b>{i.quantity} шт.</b>\n" for i in db_items])
    tag = f"\n{loc_data['admin_tag']}" if loc_data['admin_tag'] else ""
    
    header = f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ — {'ДОСТАВКА' if order.address else 'САМОВИВІЗ'}</b> (№{order.source}-{order.id})\n({syrve_info})\n\n"
    client_info = f"👤 <b>Клієнт:</b> {order.user.first_name}\n📞 <b>Телефон:</b> {order.user.phone}\n"
    
    if order.address:
        addr = order.address
        dest = f"📍 <b>Адреса:</b> вул. {addr.street}, {addr.house_number}\n🏢 <b>Деталі:</b> кв. {addr.apartment_number}, під. {addr.entrance}\n"
    else:
        dest = f"🏪 <b>Точка:</b> {loc_data['name']}\n"

    footer = f"\n📦 <b>Товари:</b>\n{items_text}\n💰 <b>РАЗОМ: {order.total_amount} грн</b>\n💬 <b>Комент:</b> {order.comment}{tag}"
    
    full_message = header + client_info + dest + footer

    requests.post(
        f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage",
        data={
            "chat_id": os.getenv("CHAT_ID"),
            "text": full_message,
            "parse_mode": "HTML",
            "message_thread_id": loc_data["topic"],
        }
    )

def create_monobank_invoice(order):
    url = "https://api.monobank.ua/api/merchant/invoice/create"
    headers = {"X-Token": os.getenv("MONO_KEY")}

    payload = {
        "amount": int(order.total_amount * 100),
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": str(order.id),
            "destination": f"Оплата замовлення WEB-{order.id}", 
        },
        "redirectUrl": f"http://127.0.0.1:9001/order/success/WEB-{order.id}",
        "webHookUrl": "http://127.0.0.1:9001/order/mono-webhook/",
    }

    response = requests.post(url, headers=headers, json=payload)
    return response



def verify_monobank_signature(x_sign, body_text):
    """
    x_sign: значення з заголовка 'X-Sign'
    body_text: сирий текст запиту (request.body)
    """
    # Публічний ключ Monobank (отриманий з /api/merchant/pubkey)
    # Зазвичай це Base64 рядок
    PUB_KEY_BASE64 = os.getenv("MONO_PUBKEY")
    
    try:
        # 1. Декодуємо ключ та підпис
        pub_key_bytes = base64.b64decode(PUB_KEY_BASE64)
        signature_bytes = base64.b64decode(x_sign)
        
        # 2. Завантажуємо ключ
        public_key = load_der_public_key(pub_key_bytes)
        
        # 3. Перевіряємо підпис
        # Monobank підписує сирий body запиту
        public_key.verify(
            signature_bytes,
            body_text,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except Exception as e:
        print(f"Signature validation failed: {e}")
        return False