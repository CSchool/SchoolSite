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
from user_profile import views as user_profile_views
from main import views
from registration.backends.simple.views import RegistrationView
from main.forms import ExtendedRegistrationForm


class ExtendedRegistrationView(RegistrationView):
    form_class = ExtendedRegistrationForm


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^$', news_views.index, name='index'),
    url(r'^news/', include('news.urls')),
    url(r'^applications/', include('applications.urls')),
    url(r'^accounts/logout/$', views.logout, name='auth_logout'),
    url(r'^accounts/register/$', ExtendedRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/profile/$', user_profile_views.profile, name='user_profile')
]
