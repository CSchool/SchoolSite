import os

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse

from applications.models import EventApplication, PracticeExamRun


class CreateApplicationForm(forms.Form):
    group_id = forms.IntegerField(required=True)
    username = forms.CharField(required=True)


class EventApplicationGenericForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = ('grade', 'address', 'school', 'organization', 'parent_phone_numbers', 'personal_data_doc')


class EventApplicationRenderForm(EventApplicationGenericForm):
    class Meta(EventApplicationGenericForm.Meta):
        exclude = ('personal_data_doc',)


class TextDisplayWidget(forms.widgets.TextInput):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return '<p>%s</p>' % value


class VoucherForm(forms.Form):
    voucher_id = forms.CharField(required=False, label=_('Voucher ID'))
    confirm_participation = forms.BooleanField(required=False, label=_('Confirm participation'))


class EventApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = ('user', 'event', 'grade', 'address',
                  'school', 'organization', 'parent_phone_numbers', 'personal_data_doc_link',
                  'theory_score', 'practice_score', 'status', 'confirm_participation')

    theory_score = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Theory score'))
    practice_score = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Practice score'))
    personal_data_doc_link = forms.CharField(disabled=True, widget=TextDisplayWidget(),
                                             label=_('Personal data processing agreement'))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            if hasattr(instance, 'personal_data_doc') and instance.personal_data_doc:
                path = os.path.basename(instance.personal_data_doc.name)
                self.base_fields['personal_data_doc_link'].initial = '''
                    <a href="%s">%s</a>
                ''' % (reverse('applications_group_application_doc', args=[instance.id, path]), path)
            else:
                self.base_fields['personal_data_doc_link'].initial = _('Not yet uploaded')
            if hasattr(instance, 'theory_exam') and instance.theory_exam:
                self.base_fields['theory_score'].initial = "<b>%d</b> / %d (min %d)" % \
                    (instance.theory_exam.cur_score, instance.theory_exam.max_score, instance.event.theoryexam.min_score)
            else:
                self.base_fields['theory_score'].initial = _('Unavailable')
            if hasattr(instance, 'practice_exam') and instance.practice_exam:
                self.base_fields['practice_score'].initial = "<b>%d</b> / %d (min %d)" % \
                    (instance.practice_exam.cur_score, instance.practice_exam.max_score, instance.event.practiceexam.min_score)
            else:
                self.base_fields['practice_score'].initial = _('Unavailable')
        forms.ModelForm.__init__(self, *args, **kwargs)


class PracticeExamRunAdminForm(forms.ModelForm):
    class Meta:
        model = PracticeExamRun
        fields = ('user', 'ejudge_run_id', 'problem', 'language', 'report', 'size')

    language = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Language'))
    report = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Report'))
    size = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Size'))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            info = instance.info
            self.base_fields['language'].initial = info['compiler']
            self.base_fields['report'].initial = info['verbose_verdict'] + (" (%d)" % info['score'] if info['score'] else "")
            self.base_fields['size'].initial = info['size']
        forms.ModelForm.__init__(self, *args, **kwargs)