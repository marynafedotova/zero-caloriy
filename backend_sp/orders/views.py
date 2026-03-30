import json
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from goods.services.syrve_client import SyrveClient
from carts.utils import get_user_carts
from orders.services.services import build_syrve_payload, finish_order_process 
from django.views.decorators.http import require_POST
from django.db import transaction


@csrf_exempt
@require_POST
def monobank_webhook(request):
    # Отримуємо підпис із заголовка
    x_sign = request.headers.get('X-Sign')
    if not x_sign:
        return HttpResponse("No signature", status=400)

    # Валідація
    if not verify_monobank_signature(x_sign, request.body):
        logger.warning(f"Invalid signature for webhook")
        return HttpResponse("Invalid signature", status=403)

    
    data = json.loads(request.body)
    invoice_id = data.get('invoiceId')
    status = data.get('status')
        
    try:
        with transaction.atomic():
            # Використовуємо select_for_update, щоб уникнути race condition
            order = Order.objects.select_for_update().get(monobank_invoice_id=invoice_id)
            
            if status == 'success' and order.status != 'PAID':
                order.status = 'PAID'
                order.save()
                
                # Тепер запускаємо відправку в Syrve та Telegram
                print("DEBUG: Calling finish_order_process for order")
                finish_order_process(order)
                return HttpResponse("OK")
                
    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return HttpResponse("Error", status=500)

    return HttpResponse("OK")

def order_success(request, order_id):
    numeric_id = str(order_id).replace('WEB-', '').replace('web-', '')
    order = get_object_or_404(Order, id=numeric_id)

    success_statuses = ['PAID', 'COD']

    # Якщо користувач повернувся сюди після оплати
    if order.status in success_statuses:
        # 1. Видаляємо кошик з БД
        from carts.models import Cart
        get_user_carts(request).delete()
        
        # 2. Очищуємо сесію
        keys_to_pop = ['order_type', 'order_type_id', 'terminal_id']
        for key in keys_to_pop:
            request.session.pop(key, None)
            
        return render(request, 'orders/success.html', {'order': order})

    else:
        # Якщо не оплачено - показуємо сторінку "Fail"
        return render(request, 'orders/fail.html', {'order': order})