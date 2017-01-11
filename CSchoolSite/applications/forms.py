from django import forms
from applications.models import EventApplication


class CreateApplication(forms.Form):
    group_id = forms.IntegerField()


class EventApplicationGeneric(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = ['phone', 'grade', 'address', 'school']