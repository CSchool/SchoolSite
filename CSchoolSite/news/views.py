from django.http import JsonResponse
from django.shortcuts import render, Http404
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from main.models import Notification
from news.models import NewsPost

@csrf_exempt
def index(req, page="1"):
    if req.POST.get('dismiss'):
        try:
            Notification.objects.get(id=req.POST.get('dismiss')).delete()
        except:
            return JsonResponse({"status": "ERR"})
        return JsonResponse({"status": "OK"})
    try:
        page_id = int(page)
    except ValueError:
        raise Http404
    posts = list(NewsPost.objects.all())
    if req.user.is_authenticated:
        notifications = list(Notification.objects.filter(user=req.user).all())
    else:
        notifications = []
    posts.extend(notifications)

    for i, p in enumerate(posts):
        if p.TYPE == 'NEWSPOST':
            setattr(posts[i], 'news', True)
        if p.TYPE == 'NOTIFICATION':
            setattr(posts[i], 'notification', True)

    posts.sort(key=lambda p: p.created)
    posts.reverse()

    paginator = Paginator(posts, 10)
    if page_id not in paginator.page_range:
        raise Http404
    cur_page = paginator.page(page_id)
    return render(req, 'news/posts.html', {
        "news": cur_page
    })


def post(req, post_id):
    try:
        post = NewsPost.objects.get(id=post_id)
    except NewsPost.DoesNotExist:
        raise Http404
    return render(req, 'news/post.html', {
        "post": post
    })