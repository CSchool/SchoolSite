from django.forms import ModelForm, DateInput, models, Form
from registration.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm, UsernameField

from .models import User
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator


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
        label=_('Email')
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

    email = forms.EmailField(required=True, label=_('Email'), max_length=250)
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


class UserRenderForm(ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'patronymic', 'birthday', 'email', 'phone']
        widgets = {'birthday': DateInput(attrs={'class': 'datepicker'})}

    email = forms.EmailField(required=True, max_length=250)
    first_name = forms.CharField(required=True, label=_('First name'))
    last_name = forms.CharField(required=True, label=_('Last name'))

    def save(self, commit=True):
        instance = super(UserRenderForm, self).save(commit=False)
        instance.username = instance.email
        if commit:
            instance.save()
        return instance


class OnOffSwitchWidget(forms.widgets.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        return '''
<div class="onoffswitch">
    <input type="checkbox" name="{name}" class="onoffswitch-checkbox" id="{id}"{checked}>
    <label class="onoffswitch-label" for="{id}"></label>
</div>
'''.format(
            checked=' checked="checked"' if value else '',
            id=attrs.get('id', name) if attrs else name,
            name=name
    )


class UserNotificationsRenderForm(ModelForm):
    class Meta:
        model = User
        fields = ['notify_onsite', 'notify_email', 'notify_telegram']

    notify_onsite = forms.BooleanField(initial=True, required=False, label=_('Show notifications in news feed'),
                                       widget=OnOffSwitchWidget())
    notify_email = forms.BooleanField(initial=True, required=False, label=_('Send notifications to email'),
                                      widget=OnOffSwitchWidget())
    notify_telegram = forms.BooleanField(initial=True, required=False, label=_('Send notifications via Telegram bot'),
                                         widget=OnOffSwitchWidget())


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'patronymic', 'birthday', 'email', 'phone',
                  'notify_onsite', 'notify_email', 'notify_telegram']
        widgets = {'birthday': DateInput(attrs={'class': 'datepicker'})}

    email = forms.EmailField(required=True, max_length=250)
    first_name = forms.CharField(required=True, label=_('First name'))
    last_name = forms.CharField(required=True, label=_('Last name'))

    notify_onsite = forms.BooleanField(initial=True, required=False, label=_('Show notifications in news feed'),
                                       widget=OnOffSwitchWidget())
    notify_email = forms.BooleanField(initial=True, required=False, label=_('Send notifications to email'),
                                      widget=OnOffSwitchWidget())
    notify_telegram = forms.BooleanField(initial=True, required=False, label=_('Send notifications via Telegram bot'),
                                         widget=OnOffSwitchWidget())

    def save(self, commit=True):
        instance = super(UserForm, self).save(commit=False)
        if not User.objects.filter(username=instance.email).exists():
            # We should not duplicate usernames
            instance.username = instance.email
        instance.notify_onsite = self.cleaned_data['notify_onsite']
        instance.notify_email = self.cleaned_data['notify_email']
        instance.notify_telegram = self.cleaned_data['notify_telegram']
        if commit:
            instance.save()
        return instance


class RelationshipAcceptanceForm(Form):

    def __init__(self, *args, **kwargs):
        super(RelationshipAcceptanceForm, self).__init__(*args, **kwargs)

        self.fields['password'].widget.attrs['placeholder'] = ''

    password = forms.CharField(widget=forms.PasswordInput, label=_('Invitation code'))
