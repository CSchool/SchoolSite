from registration.forms import RegistrationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ExtendedRegistrationForm(RegistrationForm):
    class Meta(UserCreationForm.Meta):
        fields = [
            User.USERNAME_FIELD,
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]
    first_name = forms.CharField(widget=forms.TextInput(), label="Имя")
    last_name = forms.CharField(widget=forms.TextInput(), label="Фамилия")