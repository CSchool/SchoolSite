from django.forms import ModelForm, DateInput, models, Form
from registration.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm, UsernameField

from .models import User
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _


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


class ExtendedAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True}),
        label=_('Username or email')
    )


class ExtendedRegistrationForm(RegistrationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            # User.USERNAME_FIELD,
            'email',
            'last_name',
            'first_name',
            'patronymic',
            'password1',
            'password2'
        ]

    email = forms.EmailField(required=True, label=_('Email'))
    first_name = forms.CharField(widget=forms.TextInput(), label=_('First name'))
    last_name = forms.CharField(widget=forms.TextInput(), label=_('Last name'))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email address is already registered'))
        return email

    def save(self, commit=True):
        instance = super(ExtendedRegistrationForm, self).save(commit=False)
        instance.username = instance.email
        if commit:
            instance.save()
        return instance


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'patronymic', 'birthday', 'email', 'phone']
        widgets = {'birthday': DateInput(attrs={'class': 'datepicker'})}

    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)


class RelationshipAcceptanceForm(Form):

    def __init__(self, *args, **kwargs):
        super(RelationshipAcceptanceForm, self).__init__(*args, **kwargs)

        self.fields['password'].widget.attrs['placeholder'] = ''

    password = forms.CharField(widget=forms.PasswordInput, label=_('Invitation code'))
