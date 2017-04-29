from django.conf.urls import url, include
from applications import views
from applications.tables import EnrolledTable

urlpatterns = [
    url(r'^periods$', views.choose_period, name='applications_choose_period'),
    url(r'^periods/id(?P<period_id>[0-9]+)/enrolled$', views.view_enrolled, name='applications_view_enrolled'),
    url(r'^periods/id(?P<period_id>[0-9]+)/enroll/(?P<user_id>[0-9]+)$', views.choose_group, name='applications_choose_group'),
    url(r'^id(?P<application_id>[0-9]+)/move$', views.move_group, name='applications_move_group'),
    url(r'^id(?P<application_id>[0-9]+)$', views.group_application, name='applications_group_application'),
    url(r'^create$', views.create_application, name='applications_create_application'),
    url(r'^id(?P<application_id>[0-9]+)/edu$',
        views.group_application_edu, name='applications_group_application_edu'),
    url(r'^id(?P<application_id>[0-9]+)/edit$',
        views.group_application_edit_info, name='applications_group_application_edit_info'),
    url(r'^id(?P<application_id>[0-9]+)/doc/(?P<filename>.+)',
        views.group_application_doc, name='applications_group_application_doc'),
    url(r'^id(?P<application_id>[0-9]+)/exam/practice$',
        views.group_application_practice_exam, name='applications_group_application_practice_exam'),
    url(r'^id(?P<application_id>[0-9]+)/exam/theory',
        views.group_application_theory_exam, name='applications_group_application_theory_exam'),
    url(r'^id(?P<application_id>[0-9]+)/submit_run',
        views.group_application_submit_run, name='applications_group_application_submit_run'),
    url(r'^run/(?P<run_id>[0-9]+)/source',
        views.download_run, name='applications_download_run'),
    url(r'^run/(?P<run_id>[0-9]+)/log',
        views.run_log, name='applications_run_log'),
    url(r'^id(?P<application_id>[0-9]+)/revoke',
        views.group_application_delete_confirmation, name='applications_delete_confirmation'),
    url(r'^id(?P<application_id>[0-9]+)/do_delete',
        views.group_application_delete, name='applications_delete'),
    url(r'^id(?P<application_id>[0-9]+)/statement/(?P<problem_id>[0-9]+)/(?P<filename>.+)',
        views.group_application_view_statement, name='applications_view_statement'),
    url(r'^attachment/(?P<attachment_id>[0-9]+)/(?P<filename>.+)',
        views.period_download_attachment, name='applications_download_period_attachment'),

    url(r'^periods/id(?P<period_id>[0-9]+)/enrolled/datatables/$', EnrolledTable.as_view(),
        name='applications_enrolled_table'),
]