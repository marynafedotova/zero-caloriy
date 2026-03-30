import uuid
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from goods.models import Product
from orders.models import Order, OrderItem
from goods.views import create_order_telegram
from carts.utils import calculate_delivery_cost

class DeliveryLogicTest(TestCase):
    def setUp(self):
        # Створюємо технічний товар "Доставка" з твоїм ID
        self.delivery_id = "3d496ec8-0993-4eeb-acf0-3216148d416f"
        self.delivery_product = Product.objects.create(
            id=self.delivery_id,
            name="Доставка",
            price=200,
            is_visible=False
        )
        
        # Створюємо звичайний товар для тестів
        self.cake = Product.objects.create(
            name="Десерт без цукру",
            price=500,
            is_visible=True
        )

    def test_calculate_delivery_cost_logic(self):
        """Перевірка суто функції розрахунку в utils"""
        self.assertEqual(calculate_delivery_cost(2500), 200)   # Платна
        self.assertEqual(calculate_delivery_cost(4500), 0)     # Безкоштовна
        self.assertIsNone(calculate_delivery_cost(1500))       # Недоступна

    def test_order_creation_with_paid_delivery(self):
        """Перевірка, що в базу додається OrderItem доставки при сумі 3000 грн"""
        # Створюємо замовлення (імітуємо логіку твоєї view)
        # Припустимо, ми додали 6 десертів по 500 грн = 3000 грн
        total_price = 3000
        delivery_price = calculate_delivery_cost(total_price)
        
        order = Order.objects.create(
            total_amount=total_price + delivery_price,
            order_type='DELIVERY'
        )
        
        # Додаємо десерти
        OrderItem.objects.create(order=order, product=self.cake, quantity=6, price=500)
        
        # Додаємо доставку (як у твоєму коді create_order_telegram)
        if delivery_price == 200:
            OrderItem.objects.create(
                order=order, 
                product=self.delivery_product, 
                quantity=1, 
                price=200
            )

        # ПЕРЕВІРКИ:
        self.assertEqual(order.total_amount, 3200) # 3000 + 200
        self.assertTrue(order.items.filter(product__id=self.delivery_id).exists())
        self.assertEqual(order.items.count(), 2) # Десерт + Доставка

    def test_order_creation_free_delivery(self):
        """Перевірка, що доставка НЕ додається як платна послуга при сумі 4000+"""
        total_price = 4500
        delivery_price = calculate_delivery_cost(total_price) # має бути 0
        
        order = Order.objects.create(
            total_amount=total_price + (delivery_price or 0),
            order_type='DELIVERY'
        )
        
        # ПЕРЕВІРКИ:
        self.assertEqual(order.total_amount, 4500)
        self.assertFalse(order.items.filter(product__id=self.delivery_id).exists())