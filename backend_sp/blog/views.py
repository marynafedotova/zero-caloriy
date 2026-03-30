from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.http import JsonResponse
from blog.models import Post


def blog(request):
    all_post = Post.objects.filter(is_published=True).order_by('-created_at')

    context = {
        "all_post": all_post
    }
    return render(request, "blog/blog.html", context)


def post(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    context = {
        "post": post
    }
    return render(request, "blog/post.html", context)