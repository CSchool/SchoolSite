from django.forms import ModelForm

from .models import User
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm


class AdminUserAddForm(UserCreationForm):
    class Meta:
        model = User
        fields = '__all__'

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class AdminUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic', 'birthday', 'email', 'phone']
