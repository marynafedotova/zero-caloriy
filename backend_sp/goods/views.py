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


# def products_by_group(request, slug):
#     group = get_object_or_404(Group, slug=slug)

#     # Основні продукти
#     products = Product.objects.filter(group=group, is_included_in_menu=True, type=Product.DISH)

#     # Якщо це група модифікаторів — показати модифікатори
#     modifiers = Product.objects.filter(group=group, type=Product.MODIFIER)

#     context = {
#         "group": group,
#         "products": products,
#         "modifiers": modifiers,
#     }
#     return render(request, "goods/group_products.html", context)

def product(request, product_slug, group_slug=None):
    product = get_object_or_404(Product, slug=product_slug)

    current_product = get_object_or_404(Product, slug=product_slug)
    # Отримуємо групові модифікатори до цього продукту
    group_midifiers = GroupModifier.objects.filter(product=product)

    # Для кожного group_modifier можна отримати його дочірні модифікатори
    modifiers_data = []
    for gm in group_midifiers:
        child_mods = [child.modifier for child in gm.groupmodifierchild_set.all()]

        modifiers_data.append({
            "group_modifier": gm,
            "child_modifier": child_mods
        })
    product_variants = Product.objects.filter(name_uk__icontains=current_product.name_uk.split(' ')[0]).select_related('size')
    context = {
        "product": product,
        "child_modifiers": modifiers_data,
        "variants": product_variants,

    }
    return render(request, "goods/product.html", context)


def cart(request):
    return render(request, "goods/cart.html")



# def product_detail(request, product_slug, group_slug=None):
#     product = get_object_or_404(Product, slug=product_slug)
#     print(f"Debug: product_slug={product_slug}, group_slug={group_slug}") 

#     modifiers_data = []

#     # Якщо у продукту є група
#     if product.group:
#         # Беремо тільки групи, які є модифікаторами
#         modifier_groups = Group.objects.filter(parent__isnull=True, is_included_in_menu=True, is_group_modifier=True).order_by('order')
#         print(f"Debug: знайдено {modifier_groups.count()} modifier_groups")

#         for mg in modifier_groups:
#             # Отримуємо продукти у цій групі
#             child_products = Product.objects.filter(group=mg, is_included_in_menu=True)
#             print(f"Debug: group={mg.name}, child_products={list(child_products)}")
#             if child_products:
#                 modifiers_data.append({
#                     "modifier_group": mg,
#                     "child_products": child_products
#                 })

#     context = {
#         "product": product,
#         "modifiers_data": modifiers_data,
#     }

#     return render(request, "goods/product.html", context)

