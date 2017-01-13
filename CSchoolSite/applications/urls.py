from django.conf.urls import url, include
from applications import views

urlpatterns = [
    url(r'^choose_period$', views.choose_period, name='applications_choose_period'),
    url(r'^choose_group/period/(?P<period_id>[0-9]+)$', views.choose_group, name='applications_choose_group'),
    url(r'^confirm_group/(?P<group_id>[0-9]+)$', views.confirm_group, name='applications_confirm_group'),
    url(r'^group_application/(?P<group_id>[0-9]+)$', views.group_application, name='applications_group_application'),
    url(r'^create_application$', views.create_application, name='applications_create_application'),
    url(r'^group_application/(?P<group_id>[0-9]+)/edit_info$',
        views.group_application_edit_info, name='applications_group_application_edit_info'),
    url(r'^group_application/(?P<group_id>[0-9]+)/practice_exam$',
        views.group_application_practice_exam, name='applications_group_application_practice_exam'),
    url(r'^group_application/(?P<group_id>[0-9]+)/submit_run',
        views.group_application_submit_run, name='applications_group_application_submit_run'),
    url(r'^run/(?P<run_id>[0-9]+)/source',
        views.download_run, name='applications_download_run'),
    url(r'^delete/(?P<application_id>[0-9]+)',
        views.group_application_delete, name='applications_delete'),
]