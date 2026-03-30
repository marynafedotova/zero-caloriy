import uuid
from django.db import models
from users.models import User, Address
from goods.models import Product, Restaurant


class OrderType(models.Model):
    syrve_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100) 
    service_type = models.CharField(max_length=50) 

    def __str__(self):
        return self.name


class PaymentType(models.Model):
    syrve_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100) 
    kind = models.CharField(max_length=50) 


class Order(models.Model):

    SOURCE_CHOICES = [
        ('WEB', 'Сайт'),
        ('LOKO', 'LOKO'),
        ('BOLT', 'BOLT'),
        ('GLOVO', 'GLOVO'),
        ('TG_BOT', 'Телеграм бот'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'ОЧІКУЄМО ОПЛАТУ'),
        ('PAID', 'ОПЛАЧЕНО'),
        ('COD', 'ОПЛАТА ПРИ ОТРИМАННІ'),
    ]
    
    source = models.CharField(
        max_length=10, 
        choices=SOURCE_CHOICES, 
        default='WEB', 
        verbose_name="Джерело"
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клієнт",)
    order_type = models.ForeignKey('OrderType', on_delete=models.PROTECT, verbose_name="Тип доставки",)
    terminal_group_id = models.ForeignKey(
        'goods.Restaurant', 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Локація"
    ) 
    

    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Адреса доставки")
    comment = models.TextField(blank=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='COD', 
        verbose_name="Оплата"
    )

    payment_method = models.CharField(max_length=50,blank=True, null=True, default='cash')
    monobank_invoice_id = models.CharField(max_length=100, blank=True, null=True)

    syrve_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Замовлення {self.source}-{self.id} - {self.terminal_group_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) 