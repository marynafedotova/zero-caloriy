from django.contrib import admin
from goods.models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    єfilter_vertical = ("categories",)
