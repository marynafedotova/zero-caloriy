from django.db import models

from django.db import models
from users.models import User, Address
from goods.models import Product


class OrderType(models.Model):
    syrve_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100) 
    service_type = models.CharField(max_length=50) 

class PaymentType(models.Model):
    syrve_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100) 
    kind = models.CharField(max_length=50) 


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_type = models.ForeignKey('OrderType', on_delete=models.PROTECT)
    terminal_group_id = models.UUIDField() 
    

    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(blank=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='NEW')

    syrve_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) 