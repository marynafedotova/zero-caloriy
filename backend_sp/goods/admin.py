from django.contrib import admin
from goods.models import Product, Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    єfilter_vertical = ("categories",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', ) 
    prepopulated_fields = {'slug': ('name_en',)}