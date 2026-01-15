from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from goods.models import Product


class StaticSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return [
            "goods:catalog",        
            "goods:create-order",  
            "goods:search",          # якщо потрібна у sitemap          
            "goods:cart",
            "main:index",
            "main:about",
            "main:offer",
            "main:policy",
            "main:delivery",
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = "daily"

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        # повертає правильний урл для кожного продукту
        return reverse("goods:product", kwargs={"product_slug": obj.slug})



SITEMAPS = {
    "static": StaticSitemap,
    "products": ProductSitemap,
}
