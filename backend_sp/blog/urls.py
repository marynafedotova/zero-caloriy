from django.contrib import admin
from django.urls import path, include
from blog.views import blog, post

app_name = 'blog'

urlpatterns = [
    path('', blog, name='blog'),
    path('post/<slug:post_slug>/', post, name='post'),


]
