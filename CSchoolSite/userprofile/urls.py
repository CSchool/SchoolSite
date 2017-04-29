from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from registration.backends.simple.views import RegistrationView
from userprofile.forms import ExtendedRegistrationForm
from userprofile import views
from django.contrib.auth import views as auth_views

from userprofile.tables import RelationshipTable


class ExtendedRegistrationView(RegistrationView):
    form_class = ExtendedRegistrationForm


urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^password_change/$', auth_views.password_change, name='password_change'),
    url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^logout/$', views.logout, name='auth_logout'),
    url(r'^register/$', ExtendedRegistrationView.as_view(), name='registration_register'),
    url(r'', include('registration.backends.simple.urls')),
    url(r'^profile/$', views.profile, name='user_profile'),
    url(r'^profile/edit/$', views.edit_profile, name='user_profile_edit'),
    url(r'^profile/datatables/relationship/$', login_required(RelationshipTable.as_view()), name='relationship_table'),
    url(r'^inv_code/get$', views.get_relationship_code, name='get_relationship_code'),
    url(r'^inv_code/info$', views.relationship_code_info, name='relationship_code_info')
]
