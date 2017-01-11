from django.conf.urls import url, include
from applications import views

urlpatterns = [
    url(r'^choose_period$', views.choose_period, name='applications_choose_period'),
    url(r'^choose_group/period/(?P<period_id>[0-9]+)$', views.choose_group, name='applications_choose_group'),
    url(r'^confirm_group/(?P<group_id>[0-9]+)$', views.confirm_group, name='applications_confirm_group'),
    url(r'^group_application/(?P<group_id>[0-9]+)$', views.group_application, name='applications_group_application'),
    url(r'^create_application$', views.create_application, name='applications_create_application'),
    url(r'^group_application/edit_info/(?P<group_id>[0-9]+)$',
        views.group_application_edit_info, name='applications_group_application_edit_info'),
]