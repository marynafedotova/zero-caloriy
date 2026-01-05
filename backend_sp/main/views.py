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
    new_products = Product.objects.all().order_by('-id')[:5]
    
    random_products = Product.objects.all().order_by('?')[:5]
    
    context = {
        'new_products': new_products,
        'random_products': random_products,
    }
    return render(request, "main/index.html", context)

def about_us(request):
    return render(request, "main/aboutus.html")

def offer(request):
    return render(request, "main/public_offer.html")

def policy(request):
    return render(request, "main/privacy_policy.html")