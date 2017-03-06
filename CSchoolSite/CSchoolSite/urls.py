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

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^$', news_views.index, name='index'),
    url(r'^news/', include('news.urls')),
    url(r'^applications/', include('applications.urls')),
    url(r'^accounts/', include('userprofile.urls')),
    url('^notifications/', include(notifications.urls, namespace='notifications'), name='notification_list'),
]
