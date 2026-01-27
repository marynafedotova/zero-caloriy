"""
URL configuration for backend_sp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from backend_sp.seo.sitemaps import SITEMAPS



urlpatterns = [
    # мови, які не потребують префікса (наприклад, адмінка чи API)
 path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS, "template_name": "sitemaps/sitemap.xml"},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    ]

urlpatterns += i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', include('main.urls')), 
    path('goods/', include('goods.urls')),
    path('carts/', include('carts.urls')),

)
 
