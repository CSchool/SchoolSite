from django.shortcuts import render, Http404
from django.core.paginator import Paginator

from news.models import NewsPost


def index(req, page="1"):
    try:
        page_id = int(page)
    except ValueError:
        raise Http404
    posts = NewsPost.objects.all().order_by('-created')
    paginator = Paginator(posts, 10)
    if page_id not in paginator.page_range:
        raise Http404
    cur_page = paginator.page(page_id)
    return render(req, 'news/posts.html', {
        "news": cur_page,
        "total_pages": paginator.num_pages,
        "current_page": page_id
    })


def post(req, post_id):
    try:
        post = NewsPost.objects.get(id=post_id)
    except NewsPost.DoesNotExist:
        raise Http404
    return render(req, 'news/post.html', {
        "post": post
    })