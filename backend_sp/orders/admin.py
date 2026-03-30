from django.contrib import admin
from orders.models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem

    fields = ['product', 'quantity', 'price', 'get_row_total']
    readonly_fields = ['get_row_total'] 
    extra = 0


    def get_row_total(self, obj):
        if obj.quantity and obj.price:
            return obj.quantity * obj.price
        return 0
    

    get_row_total.short_description = 'Сума (грн)'



@admin.register(Order)
class OrdertAdmin(admin.ModelAdmin):
    list_display = ( '__str__', 'user', 'created_at')
    search_fields = ('id', )
    inlines = [OrderItemInline]

