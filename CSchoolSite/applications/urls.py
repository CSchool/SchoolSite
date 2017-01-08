from django.conf.urls import url, include
from applications import views

urlpatterns = [
    url(r'^choose_period$', views.choose_period, name='applications_choose_period'),
    url(r'^choose_group/period/(?P<period_id>[0-9]+)$', views.choose_group, name='applications_choose_group'),
]