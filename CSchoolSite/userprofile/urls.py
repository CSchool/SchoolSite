from django.conf.urls import include, url
from registration.backends.simple.views import RegistrationView
from userprofile.forms import ExtendedRegistrationForm
from userprofile import views


class ExtendedRegistrationView(RegistrationView):
    form_class = ExtendedRegistrationForm


urlpatterns = [
    url(r'^logout/$', views.logout, name='auth_logout'),
    url(r'^register/$', ExtendedRegistrationView.as_view(), name='registration_register'),
    url(r'', include('registration.backends.simple.urls')),
    url(r'^profile/$', views.profile, name='user_profile'),
    url(r'^profile/edit/$', views.edit_profile, name='user_profile_edit')
]
