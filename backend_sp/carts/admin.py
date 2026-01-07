from django.contrib import admin
from carts.models import Cart

@admin.register(Cart)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('create',)