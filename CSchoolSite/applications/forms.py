import os

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse
from django.contrib.admin.widgets import AdminDateWidget

from applications.models import EventApplication, PracticeExamRun, Event
from userprofile.models import User


class TextDisplayWidget(forms.widgets.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, bool):
            return '<p>%s</p>' % (_('Yes') if value else _('No'))
        if not value:
            return '<i>%s</i>' % _('Unknown')
        return '<p>%s</p>' % value


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['coordinators'].queryset = User.objects.filter(is_staff=True).all()


class CreateApplicationForm(forms.Form):
    group_id = forms.IntegerField(required=True)
    username = forms.CharField(required=True)


class EventApplicationGenericForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = ('student_inititals', 'grade', 'address', 'birthday', 'organization',
                  'parent_phone_numbers', 'personal_laptop', 'voucher_parent', 'personal_data_doc')

    FIELDS = ('grade', 'address', 'organization', 'parent_phone_numbers',
              'personal_laptop', 'voucher_parent')

    student_inititals = forms.CharField(required=False, label=_('Student\'s initials'), widget=TextDisplayWidget())
    birthday = forms.DateField(required=True, label=_('birthday'),
                               widget=forms.DateInput(attrs={'class': 'datepicker'}))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            self.base_fields['student_inititals'].initial = instance.user.get_initials()
            self.base_fields['birthday'].initial = instance.user.birthday

            for field in EventApplicationGenericForm.FIELDS:
                self.base_fields[field].initial = getattr(instance, field, None)

        forms.ModelForm.__init__(self, *args, **kwargs)

    def save(self, commit=True):
        instance = super(EventApplicationGenericForm, self).save(commit=False)
        instance.user.birthday = self.cleaned_data['birthday']
        instance.user.save()
        if commit:
            instance.save()
        return instance



class EventApplicationPrivForm(EventApplicationGenericForm):
    class Meta(EventApplicationGenericForm.Meta):
        fields = ('student_inititals', 'grade', 'address', 'birthday', 'organization',
                  'parent_phone_numbers', 'personal_laptop', 'voucher_parent', 'personal_data_doc', 'voucher_id')

    voucher_id = forms.CharField(required=True, label=_('Voucher ID'))


class EventApplicationVoucherForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = ('voucher_id',)

    voucher_id = forms.CharField(required=True, label=_('Voucher ID'))


class EventApplicationRenderForm(EventApplicationGenericForm):
    class Meta(EventApplicationGenericForm.Meta):
        exclude = ('personal_data_doc',)



class VoucherForm(forms.Form):
    voucher_id = forms.CharField(required=False, label=_('Voucher ID'))
    confirm_participation = forms.BooleanField(required=False, label=_('Confirm participation'))


class EventApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = ('student_initials', 'group', 'grade', 'address',
                  'birthday', 'organization', 'parent_phone_numbers', 'voucher_parent',
                  'personal_data_doc_link', 'personal_laptop',
                  'theory_score', 'practice_score', 'status', 'denial_reason', 'submitted_at',
                  'issued_at', 'issued_by')

    student_initials = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Student\'s initials'))
    group = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Group'))
    theory_score = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Theory score'))
    practice_score = forms.CharField(disabled=True, widget=TextDisplayWidget(), label=_('Practice score'))
    birthday = forms.DateField(required=False, label=_('birthday'), widget=AdminDateWidget())
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
            self.base_fields['student_initials'].initial = instance.user.get_initials()
            self.base_fields['group'].initial = instance.event.__str__()
            self.base_fields['birthday'].initial = instance.user.birthday
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

    def save(self, commit=True):
        instance = super(EventApplicationAdminForm, self).save(commit=False)
        instance.user.birthday = self.cleaned_data['birthday']
        instance.user.save()
        if commit:
            instance.save()
        return instance


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