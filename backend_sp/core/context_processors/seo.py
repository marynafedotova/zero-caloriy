from django.utils.translation import get_language
from django.urls import resolve
from django.conf import settings

def seo_tags(request):
    current_lang = get_language()  # 'uk' или 'ru'
    path = request.get_full_path()  # текущий путь, например /uk/product-1/

    # Домены вашего сайта
    base_domains = {
        'uk': 'https://zerokaloriy.com/uk',
        'ru': 'https://zerokaloriy.com/ru',
    }

    canonical_url = f"{base_domains[current_lang]}{path[len(f'/{current_lang}'):]}"  # убираем язык из path, если нужно

    # Alternate URLs для hreflang
    alternate_urls = {}
    for lang_code, domain in base_domains.items():
        # path без префикса языка
        path_without_lang = path
        if path.startswith(f'/{current_lang}/'):
            path_without_lang = path[len(f'/{current_lang}'):]
        alternate_urls[lang_code] = f"{domain}{path_without_lang}"

    return {
        'canonical_url': canonical_url,
        'alternate_urls': alternate_urls,
        'current_lang': current_lang,
    }
