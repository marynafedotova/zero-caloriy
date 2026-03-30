from django.contrib import admin
from django.urls import path, include
from main.views  import set_language, index, about_us, offer, policy, delivery, thank_you

app_name = 'main'


urlpatterns = [
    path("set-language/", set_language, name="set_lang"),
    path("", index, name="index"),
    path("about-us/", about_us, name="about"),
    path("public-offer/", offer, name="offer"),
    path("privacy-policy/", policy, name="policy"),
    path("delivery/", delivery, name="delivery"),
    path("thank-you/", thank_you, name="thank_you"),
    
]

