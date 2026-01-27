from django.db import models
from goods.models import Product
from users.models import User

class CarQueryset(models.QuerySet):

    def total_prace(self):
        return sum(cart.product_prace() for cart in self)
    
    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)
        
        return 0

class Cart(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)
    session_key = models.CharField(max_length=32, null=True, blank=True)
    chat_id = models.BigIntegerField(null=True, blank=True)
    create = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"
        ordering = ["create"]
    
    objects = CarQueryset().as_manager()

    def product_prace(self):
        return round(self.product.price * self.quantity)

    def __str__(self):
        return f"{self.create}"
