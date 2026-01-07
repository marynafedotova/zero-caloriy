from django.shortcuts import render, get_object_or_404
from .models import Product, Group, GroupModifier, GroupModifierChild
from django.db.models import Q


def catalog(request):
    products = Product.objects.filter(is_included_in_menu=True)
    groups = Group.objects.filter(is_included_in_menu=True, parent__isnull=True).order_by('order')
    context = {
        'products': products,
        'groups': groups,  # для меню
    }
    return render(request, "goods/catalog.html", context)


def product(request, product_slug, group_slug=None):
    # Отримуємо основний продукт один раз
    product = get_object_or_404(Product, slug=product_slug)
    
    #отримання модифікаторів (використовуємо prefetch_related)
    group_modifiers = GroupModifier.objects.filter(product=product).prefetch_related(
        'groupmodifierchild_set__modifier'
    )

    modifiers_data = []
    for gm in group_modifiers:
        modifiers_data.append({
            "group_modifier": gm,
            "child_modifiers": [child.modifier for child in gm.groupmodifierchild_set.all()],
        })

    # Пошук варіантів (вага/розмір)
    first_word = product.name_uk.split(' ')[0]
    product_variants = Product.objects.filter(
        name_uk__icontains=first_word,
        size__isnull=False 
    ).select_related('size').order_by('weight')

    if not product_variants.exists():
        product_variants = [product]

    
    random_products = Product.objects.exclude(id=product.id).order_by('?')[:5]

    context = {
        "product": product,
        "child_modifiers": modifiers_data,
        "variants": product_variants,
        "random_products": random_products,
    }
    return render(request, "goods/product.html", context)


def cart(request):
    return render(request, "goods/cart.html")



def product_search(request):
    query = request.GET.get('q', '').strip()
    
    if query:
        products = Product.objects.filter(
            Q(name_uk__icontains=query) | 
            Q(name_en__icontains=query) |
            Q(name_ru__icontains=query) |
            Q(description_uk__icontains=query) | 
            Q(description_en__icontains=query) |
            Q(description_ru__icontains=query)     
        ).distinct() 
    else:

        products = Product.objects.none()

    context = {
        'goods': products, 
        'query': query,
    }
    

    return render(request, 'goods/search_results.html', context)