from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from goods.models import Product, Category, ProductCategory, Restaurant
from goods.services.syrve_client import SyrveClient


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Відображення списку всіх товарів
    list_display = ('name_uk', 'size',  'price', 'is_visible')
    list_filter = ('is_visible', 'is_manual_params', 'size')
    search_fields = ('name_uk', 'name_en', 'name_ru', 'code', 'slug')
    prepopulated_fields = {'slug': ('name_uk',)}
    
    # Групування полів усередині картки товару
    fieldsets = (
        ('Статус', {
            'fields': (
                'is_visible', 
                'is_manual_params', 
            )
        }),
                ('Українська версія (UK)', {
            'fields': (
                'name_uk', 
                'description_uk', 
                'additional_info_uk', 
                'about_product_uk'
            ),
        }),
        ('Русская версия (RU)', {
            'fields': (
                'name_ru', 
                'description_ru', 
                'additional_info_ru', 
                'about_product_ru',
                'measure_unit_ru'
            ),
            'classes': ('collapse',), 
        }),
        ('English Version (EN)', {
            'fields': (
                'name_en', 
                'description_en', 
                'additional_info_en', 
                'about_product_en',
                'measure_unit_en'
            ),
            'classes': ('collapse',), 
        }),
        ('Ціна та параметри', {
            'fields': (
                'price', 
                'weight', 
                'size', 
                'measure_unit_uk'
            )
        }),
        ('Класифікація та медіа', {
            'fields': (
                'group', 
                'product_category', 
                'categories', 
                'image_url', 
            )
        }),     
        ('Дати створення/оновлення', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
        ('Системні дані', {
            'fields': (
                'code', 
                'slug', 
                'type', 
                'payment_subject',
                'order'
            ),
            'classes': ('collapse',),
        }),
    )

    # Робимо дати тільки для читання, бо auto_now_add не дає їх редагувати
    readonly_fields = ('created', 'updated')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sync-syrve/', self.admin_site.admin_view(self.sync_syrve), name='sync_syrve_products'),
        ]
        return custom_urls + urls


    def sync_syrve(self, request):
        try:
            client = SyrveClient()
            client.save_menu_from_db()
            self.message_user(request, "✅ Товари та категорії Syrve синхронізовано!", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"❌ Помилка синхронізації: {str(e)}", messages.ERROR)
        

        return redirect("admin:goods_product_changelist")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', ) 

    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', ) 


