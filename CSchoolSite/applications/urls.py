from django.conf.urls import url, include
from applications import views

urlpatterns = [
    url(r'^choose_period$', views.choose_period, name='applications_choose_period'),
]