from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils import translation
from goods.models import Product


def set_language(request):
    lang = request.GET.get("lang", "uk")
    translation.activate(lang)

    response = HttpResponseRedirect(
        request.META.get("HTTP_REFERER", "/")
    )
    response.set_cookie("lang", lang)
    return response

def index(request):
    new_products = Product.objects.filter(is_visible=True).order_by('-id')[:5]
    
    random_products = Product.objects.filter(is_visible=True).order_by('?')[:5]

    all_products = list(new_products) + [p for p in random_products if p not in new_products]
    context = {
        'new_products': new_products,
        'random_products': random_products,
        'all_products': all_products,
    }
    return render(request, "main/index.html", context)

def about_us(request):
    return render(request, "main/aboutus.html")

def offer(request):
    return render(request, "main/public_offer.html")

def policy(request):
    return render(request, "main/privacy_policy.html")

def delivery(request):
    return render(request, "main/delivery.html")

def thank_you(request):
    return render(request, "main/thank_you.html")