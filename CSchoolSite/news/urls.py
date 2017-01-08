from django.conf.urls import url, include
from news import views

urlpatterns = [
    url(r'^$', views.index, name='news'),
    url(r'^page/(?P<page>[0-9]+)$', views.index, name='news_paged'),
    url(r'^post/(?P<post_id>[0-9]+)$', views.post, name='news_post')
]