from django.db import models
import uuid



class User(models.Model):
    user_id = models.BigIntegerField(unique=True, primary_key=True)
    language = models.CharField(max_length=10, default='uk')
    
    # 1 Етап Контакти + Адреса
    first_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
      

    # 2 Етап Лояльність
    email = models.EmailField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    is_loyalty_member = models.BooleanField(default=False)

    # Технічні поля
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.first_name or 'User'} ({self.user_id})"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    city = models.CharField(max_length=100, default='Київ')
    street = models.CharField(max_length=255)
    house_number = models.CharField(max_length=20)
    apartment_number = models.CharField(max_length=20, blank=True, null=True)
    entrance = models.CharField(max_length=20, blank=True, null=True)
    floor = models.CharField(max_length=10, blank=True, null=True)
    is_default = models.BooleanField(default=False) # Щоб пропонувати останню використану

    def __str__(self):
        return f"{self.street}, {self.house_number}"