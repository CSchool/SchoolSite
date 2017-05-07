"""CSchoolSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from news import views as news_views
import notifications.urls

from CSchoolSite import settings
from main.views import serve_admin_media

urlpatterns = [
    url('', include('social_django.urls', namespace='social')),
    url(r'^admin/', admin.site.urls),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^$', news_views.index, name='index'),
    url(r'^news/', include('news.urls')),
    url(r'^applications/', include('applications.urls')),
    url(r'^accounts/', include('userprofile.urls')),
    url('^notifications/', include(notifications.urls, namespace='notifications'), name='notification_list'),
    url('^{}(?P<path>.*)$'.format(settings.MEDIA_URL[1:] if settings.MEDIA_URL[0] == '/' else settings.MEDIA_URL),
        serve_admin_media, {'document_root': settings.MEDIA_ROOT}),
]

try:
    import telegram.views
    urlpatterns.append(url(r'^telegram_auth/(?P<chat_id>[0-9]+)_(?P<checksum>[0-9a-f]+)',
                           telegram.views.auth_view, name='telegram_auth'))
    urlpatterns.append(url(r'^telegram_unlink',
                           telegram.views.unlink_view, name='telegram_unlink'))
except ImportError:
    pass
