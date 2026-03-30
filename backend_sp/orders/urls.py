from django.urls import path
from orders.views import order_success, monobank_webhook

app_name = 'orders'

urlpatterns = [
    path('success/<str:order_id>/', order_success, name='order_success'),
    path('mono-webhook/', monobank_webhook, name='monobank_webhook'),



]
