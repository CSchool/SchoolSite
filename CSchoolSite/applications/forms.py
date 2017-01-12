from django import forms
from applications.models import EventApplication


class CreateApplicationForm(forms.Form):
    group_id = forms.IntegerField()


class EventApplicationGenericForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = ['phone', 'grade', 'address', 'school']