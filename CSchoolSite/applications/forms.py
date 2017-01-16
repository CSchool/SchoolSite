from django import forms
from django.utils.translation import ugettext_lazy as _

from applications.models import EventApplication


class CreateApplicationForm(forms.Form):
    group_id = forms.IntegerField()


class EventApplicationGenericForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = ('phone', 'grade', 'address', 'school')


class TextDisplayWidget(forms.widgets.TextInput):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return '<p>%s</p>' % value


class EventApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = ('user', 'event', 'phone', 'grade', 'address', 'school', 'theory_score', 'practice_score')

    theory_score = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Theory score'))
    practice_score = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Practice score'))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            if instance.theory_exam:
                self.base_fields['theory_score'].initial = "<b>%d</b> / %d (min %d)" % \
                    (instance.theory_exam.cur_score, instance.theory_exam.max_score, instance.event.theoryexam.min_score)
            if instance.practice_exam:
                self.base_fields['practice_score'].initial = "<b>%d</b> / %d (min %d)" % \
                    (instance.practice_exam.cur_score, instance.practice_exam.max_score, instance.event.practiceexam.min_score)
        forms.ModelForm.__init__(self, *args, **kwargs)