from django.urls import reverse

import ejudge
import uuid
import os

from django import forms
from django.db import models
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from CSchoolSite import settings


def get_file_path(prefix):
    def f(instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return os.path.join(prefix, filename)
    return f


class Period(models.Model):
    class Meta:
        verbose_name = _('Period')
        verbose_name_plural = _('Periods')
        permissions = (
            ("view_period", _("view periods")),
        )

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    begin = models.DateTimeField(verbose_name=_('Period begins'))
    end = models.DateTimeField(verbose_name=_('Period ends'))
    registration_begin = models.DateTimeField(verbose_name=_('Registration begins'))
    registration_end = models.DateTimeField(verbose_name=_('Registration ends'))

    def __str__(self):
        return self.name

    @property
    def registration_open(self):
        if self.registration_begin <= timezone.now() <= self.registration_end:
            return True
        return False

    @property
    def registration_started(self):
        if self.registration_begin <= timezone.now():
            return True
        return False

    @property
    def ongoing(self):
        if self.begin <= timezone.now() <= self.end:
            return True
        return False

    @property
    def began(self):
        if self.begin <= timezone.now():
            return True
        return False

    @property
    def ended(self):
        if timezone.now() > self.end:
            return True
        return

    def get_application_status(self, user):
        try:
            application = EventApplication.objects.get(user=user, event__period=self,
                                                       event__type=Event.CLASS_GROUP)
        except EventApplication.DoesNotExist:
            return "NA", "Not applicable", None
        return application.status, application.get_status_display(), application.id


class PeriodAttachment(models.Model):
    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    def get_upload_path(self, filename):
        return os.path.join('attachments', 'period_%d' % self.period.id, filename)

    def get_url(self):
        return reverse('applications_download_period_attachment', args=[self.id, os.path.basename(self.file.name)])

    def get_name(self):
        return os.path.basename(self.file.name)

    AGREEMENT = 'AG'
    OTHER = 'OT'

    ATTACHMENT_TYPE_CHOICES = (
        (AGREEMENT, _('Personal data processing agreement')),
        (OTHER, _('Other'))
    )

    type = models.CharField(max_length=2, choices=ATTACHMENT_TYPE_CHOICES,
                            default=OTHER, verbose_name=_('Attachment type'))

    name = models.CharField(max_length=250, verbose_name=_('Name'))
    file = models.FileField(verbose_name=_('File'), upload_to=get_upload_path)
    period = models.ForeignKey('Period', on_delete=models.CASCADE, verbose_name=_('Period'))

    def __str__(self):
        return self.period.name + ' - ' + self.name


class Event(models.Model):
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    period = models.ForeignKey('Period', on_delete=models.CASCADE, verbose_name=_('Period'))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='EventApplication', through_fields=('event', 'user'))
    description = models.TextField(verbose_name=_('Description'))
    # begin = models.DateTimeField(verbose_name=_('Event begins'))
    # end = models.DateTimeField(verbose_name=_('Event ends'))
    # registration_begin = models.DateTimeField(verbose_name=_('Registration begins'))
    # registration_end = models.DateTimeField(verbose_name=_('Registration ends'))
    category = models.CharField(max_length=100, verbose_name=_('Category'), blank=True, default='')
    is_open = models.BooleanField(verbose_name=_('Registration open'))
    limit = models.IntegerField(verbose_name=_('Participants limit'))
    difficulty = models.IntegerField(verbose_name=_('Relative difficulty'), default=0)

    # Event type
    CLASS_GROUP = 'CL'
    CAMP_GROUP = 'CA'
    OLYMP = 'OL'

    EVENT_TYPE_CHOICES = (
        (CLASS_GROUP, _('Class group')),
        (CAMP_GROUP, _('Camp group')),
        (OLYMP, _('Tournament'))
    )

    type = models.CharField(max_length=2, choices=EVENT_TYPE_CHOICES, default=CLASS_GROUP, verbose_name=_('Event type'))

    def __str__(self):
        return self.name + ' - ' + self.period.name

    @property
    def registration_open(self):
        if self.registration_begin <= timezone.now() <= self.registration_end and self.is_open:
            return True
        return False


class PracticeExam(models.Model):
    class Meta:
        verbose_name = _('Practice exam')
        verbose_name_plural = _('Practice exams')

    rand_problems = models.IntegerField(verbose_name=_('Random problems'))
    slot_problems = models.IntegerField(verbose_name=_('Slot problems'))
    min_score = models.IntegerField(verbose_name=_('Minimum total score'))
    event = models.OneToOneField(Event)

    def __str__(self):
        return self.event.__str__()


class PracticeExamProblem(models.Model):
    class Meta:
        verbose_name = _('Practice exam problem')
        verbose_name_plural = _('Practice exams problems')

    name = models.CharField(max_length=250, verbose_name=_('Problem name'))
    ejudge_id = models.CharField(max_length=100, verbose_name=_('Problem id'), unique=True)
    slot = models.IntegerField(verbose_name=_('Problem slot'))
    statement = models.FileField(verbose_name=_('Statement'), blank=True)
    score = models.IntegerField(verbose_name=_('Problem score'))

    exam = models.ForeignKey(PracticeExam, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def available_compilers(self):
        return ejudge.get_available_compilers()


class PracticeExamRun(models.Model):
    class Meta:
        verbose_name = _('Practice exam run')
        verbose_name_plural = _('Practice exams runs')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ejudge_run_id = models.IntegerField(verbose_name=_('Run ID'), unique=True)
    problem = models.ForeignKey(PracticeExamProblem, on_delete=models.CASCADE)
    submitted = models.DateTimeField(auto_now_add=True, verbose_name=_('Submitted at'))

    def __str__(self):
        return self.user.get_full_name() + " - " + self.problem.name

    @property
    def info(self):
        return ejudge.get_run_info(self.ejudge_run_id)

    @property
    def compile_log(self):
        return ejudge.get_compiler_log(self.ejudge_run_id)

    @staticmethod
    def submit(request, problem_id, lang_id, filename):
        try:
            problem = PracticeExamProblem.objects.get(ejudge_id=problem_id)
        except PracticeExamProblem.DoesNotExist:
            return None
        run_id = ejudge.submit_run(problem_id, lang_id, filename)
        if run_id is None:
            return None
        run = PracticeExamRun()
        run.user = request.user
        run.ejudge_run_id = run_id
        run.problem = problem
        run.save()
        return run


class PracticeExamApplication(models.Model):
    # TODO: Should it be visible in admin panel?
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problems = models.ManyToManyField(PracticeExamProblem, through='PracticeExamApplicationProblem')
    application = models.OneToOneField('EventApplication', related_name='practice_exam')

    @staticmethod
    def generate_for_user(user, practice_exam):
        try:
            application = EventApplication.objects.get(user=user, event=practice_exam.event,
                                                       event__type=Event.CLASS_GROUP)
        except EventApplication.DoesNotExist:
            application = EventApplication()
            application.user = user
            application.event = practice_exam.event
        exam_application = PracticeExamApplication()
        exam_application.user = user
        exam_application.application = application
        exam_application.save()
        application.practice_exam = exam_application
        application.save()
        for slot in range(1, practice_exam.slot_problems + 1):
            try:
                problems = PracticeExamProblem.objects.filter(exam=practice_exam, slot=slot).all()
            except PracticeExamProblem.DoesNotExist:
                continue
            if len(problems) > 0:
                from random import randint
                problem = problems[randint(0, len(problems) - 1)]
                a_problem = PracticeExamApplicationProblem()
                a_problem.problem = problem
                a_problem.index = slot
                a_problem.application = exam_application
                a_problem.save()
        try:
            from random import shuffle
            problems = PracticeExamProblem.objects.filter(exam=practice_exam, slot=0).all()
            problems = list(problems)
            shuffle(problems)
            idx = practice_exam.slot_problems + 1
            for problem in problems[:practice_exam.rand_problems]:
                a_problem = PracticeExamApplicationProblem()
                a_problem.problem = problem
                a_problem.index = idx
                a_problem.application = exam_application
                a_problem.save()
                idx += 1
        except PracticeExamProblem.DoesNotExist:
            pass
        return exam_application

    @property
    def solved_problems(self):
        runs = PracticeExamRun.objects.filter(user=self.user, problem__practiceexamapplication=self).all()
        solved = {}
        for run in runs:
            info = run.info
            if info['verdict'] == 'OK':
                solved[info['problem']] = True
        return len(solved)

    @property
    def total_problems(self):
        return self.problems.all().count()

    @property
    def cur_score(self):
        runs = PracticeExamRun.objects.filter(user=self.user, problem__practiceexamapplication=self).all()
        solved = {}
        score = 0
        for run in runs:
            info = run.info
            if info['verdict'] == 'OK':
                if info['problem'] not in solved:
                    score += run.problem.score
                solved[info['problem']] = True
        return score

    @property
    def passed(self):
        return self.cur_score >= self.application.event.practiceexam.min_score

    @property
    def percentage(self):
        return "%d%%" % round(self.cur_score * 100 / self.max_score)

    @property
    def max_score(self):
        return self.problems.aggregate(models.Sum('score'))['score__sum']


class PracticeExamApplicationProblem(models.Model):
    # TODO: Should it be visible in admin panel?
    class Meta:
        ordering = ('index',)

    application = models.ForeignKey(PracticeExamApplication, on_delete=models.CASCADE)
    problem = models.ForeignKey(PracticeExamProblem, on_delete=models.CASCADE)
    index = models.IntegerField()


class TheoryExam(models.Model):
    class Meta:
        verbose_name = _('Theory exam')
        verbose_name_plural = _('Theory exams')

    rand_questions = models.IntegerField(verbose_name=_('Random questions'))
    slot_questions = models.IntegerField(verbose_name=_('Slot questions'))
    min_score = models.IntegerField(verbose_name=_('Minimum total score'))
    event = models.OneToOneField(Event)

    def __str__(self):
        return self.event.__str__()


class TheoryExamQuestion(models.Model):
    class Meta:
        verbose_name = _('Theory exam question')
        verbose_name_plural = _('Theory exams questions')

    title = models.CharField(max_length=100, verbose_name=_('Name'))
    question = models.TextField(verbose_name=_('Question'))
    answer = models.CharField(max_length=100, verbose_name=_('Answer'))
    trim_answer = models.BooleanField(default=True, verbose_name=_('Remove extra spaces from answer'))
    case_sensitive_answer = models.BooleanField(default=False, verbose_name=_('Answer is case-sensitive'))
    exam = models.ForeignKey(TheoryExam, on_delete=models.CASCADE)
    slot = models.IntegerField(verbose_name=_('Question slot'))
    score = models.IntegerField(verbose_name=_('Score'), default=0)

    # Question type
    NUMBER = 'NB'
    TEXT = 'TX'
    CHOICE = 'CH'
    MULTICHOICE = 'MC'

    THEORY_EXAM_QUESTION_TYPE_CHOICES = (
        (NUMBER, _('Integer number as an answer')),
        (TEXT, _('String as an answer')),
        (CHOICE, _('One option as an answer')),
        (MULTICHOICE, _('Several options as an answer')),
    )

    qtype = models.CharField(max_length=2, choices=THEORY_EXAM_QUESTION_TYPE_CHOICES,
                             default=TEXT, verbose_name=_('Answer type'))

    def __str__(self):
        return self.title

    @property
    def django_form(self):
        if self.qtype == TheoryExamQuestion.NUMBER:
            class DynForm(forms.Form):
                answer = forms.IntegerField(label=_('Answer'), required=True,
                                            widget=forms.TextInput(attrs={'autocomplete': 'off'}))
        if self.qtype == TheoryExamQuestion.TEXT:
            class DynForm(forms.Form):
                answer = forms.CharField(label=_('Answer'), required=True,
                                         widget=forms.TextInput(attrs={'autocomplete': 'off'}))
        if self.qtype == TheoryExamQuestion.CHOICE:
            choices = [(x.short, x.option) for x in self.theoryexamquestionoption_set.all()]

            class DynForm(forms.Form):
                answer = forms.ChoiceField(choices=choices, required=True, label=_('Answer'),
                                           widget=forms.RadioSelect(attrs={'autocomplete': 'off'}))
        if self.qtype == TheoryExamQuestion.MULTICHOICE:
            choices = [(x.short, x.option) for x in self.theoryexamquestionoption_set.all()]

            class DynForm(forms.Form):
                answer = forms.MultipleChoiceField(choices=choices, required=True, label=_('Answer'),
                                                   widget=forms.CheckboxSelectMultiple(attrs={'autocomplete': 'off'}))
        return DynForm


class TheoryExamQuestionOption(models.Model):
    class Meta:
        verbose_name = _('Possible answer')
        verbose_name_plural = _('Possible answers')
        ordering = ('short',)

    question = models.ForeignKey(TheoryExamQuestion, on_delete=models.CASCADE)
    option = models.CharField(max_length=100, verbose_name=_('Possible answer'))
    short = models.CharField(max_length=15, verbose_name=_('Short ID'))
    correct = models.BooleanField(verbose_name=_('This answer is correct'))

    def __str__(self):
        return Truncator(self.option).chars(50)


class TheoryExamApplicationQuestion(models.Model):
    # TODO: Should it be visible in admin panel?
    class Meta:
        ordering = ('index',)

    application = models.ForeignKey('TheoryExamApplication', on_delete=models.CASCADE)
    question = models.ForeignKey('TheoryExamQuestion', on_delete=models.CASCADE)
    index = models.IntegerField()
    answer = models.CharField(max_length=100, null=True, blank=True)

    @property
    def django_form(self):
        DynForm = self.question.django_form
        ans = self.answer
        if self.answer is not None:
            if self.question.qtype == TheoryExamQuestion.MULTICHOICE:
                ans = self.answer.split(',')
        form = DynForm(dict(answer=ans))
        if not form.is_valid():
            return None
        return form


class TheoryExamApplication(models.Model):
    # TODO: Should it be visible in admin panel?
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questions = models.ManyToManyField(TheoryExamQuestion, through='TheoryExamApplicationQuestion')
    application = models.OneToOneField('EventApplication', related_name='theory_exam')

    @staticmethod
    def generate_for_user(user, theory_exam):
        try:
            application = EventApplication.objects.get(user=user, event=theory_exam.event,
                                                       event__type=Event.CLASS_GROUP)
        except EventApplication.DoesNotExist:
            application = EventApplication()
            application.user = user
            application.event = theory_exam.event
        exam_application = TheoryExamApplication()
        exam_application.user = user
        exam_application.application = application
        exam_application.save()
        application.theory_exam = exam_application
        application.save()
        for slot in range(1, theory_exam.slot_questions + 1):
            try:
                questions = TheoryExamQuestion.objects.filter(exam=theory_exam, slot=slot).all()
            except TheoryExamQuestion.DoesNotExist:
                continue
            if len(questions) > 0:
                from random import randint
                question = questions[randint(0, len(questions) - 1)]
                a_question = TheoryExamApplicationQuestion()
                a_question.question = question
                a_question.index = slot
                a_question.application = exam_application
                a_question.save()
        try:
            from random import shuffle
            questions = TheoryExamQuestion.objects.filter(exam=theory_exam, slot=0).all()
            questions = list(questions)
            shuffle(questions)
            idx = theory_exam.slot_questions + 1
            for question in questions[:theory_exam.rand_questions]:
                a_question = TheoryExamApplicationQuestion()
                a_question.question = question
                a_question.index = slot
                a_question.application = exam_application
                a_question.save()
                idx += 1
        except TheoryExamQuestion.DoesNotExist:
            pass
        return exam_application

    @property
    def answered_questions(self):
        return TheoryExamApplicationQuestion.objects.filter(application=self) \
            .exclude(answer='').exclude(answer__isnull=True).count()

    @property
    def total_questions(self):
        return self.questions.all().count()

    @property
    def cur_score(self):
        score = 0
        for question in TheoryExamApplicationQuestion.objects.filter(application=self).all():
            if question.question.qtype == TheoryExamQuestion.MULTICHOICE:
                ans = question.answer.split(',')
                total = question.question.theoryexamquestionoption_set.count()
                ok = question.question.theoryexamquestionoption_set.filter(correct=True, short__in=ans).count() \
                     + question.question.theoryexamquestionoption_set.filter(correct=False).exclude(
                    short__in=ans).count()
                score += ok * question.question.score // total
            else:
                if question.question.answer == question.answer:
                    score += question.question.score
        return score

    @property
    def passed(self):
        return self.cur_score >= self.application.event.theoryexam.min_score

    @property
    def percentage(self):
        return "%d%%" % round(self.cur_score * 100 / self.max_score)

    @property
    def max_score(self):
        return self.questions.aggregate(models.Sum('score'))['score__sum']


class EventApplication(models.Model):
    class Meta:
        verbose_name = _('Event application')
        verbose_name_plural = _('Event applications')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    grade = models.IntegerField(choices=[(i, i) for i in range(1, 12)],
                                null=True, verbose_name=_('Grade'), help_text=_("Current grade"))
    address = models.TextField(null=True, verbose_name=_('Home address'))
    school = models.CharField(max_length=50, null=True,
                              verbose_name=_('School'), help_text=_("e.g. School №42"))

    organization = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Organization'))
    parent_phone_numbers = models.TextField(null=True, blank=True, verbose_name=_("Parents' phone numbers"))
    personal_laptop = models.BooleanField(default=False, blank=True, verbose_name=_('Personal laptop will be used'))
    personal_data_doc = models.FileField(null=True, verbose_name=_('Personal data processing agreement'))

    voucher_parent = models.CharField(max_length=250, null=True, verbose_name=_('Parent\'s full name'),
                                      help_text=_('Full name of the parent to whom the voucher is drawn up'))

    voucher_id = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('Voucher ID'))

    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Submitted at'), default=None)

    issued_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Issued at'), default=None)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=_('Issued by'), default=None,
                                  related_name='issued_applications', related_query_name='issued_application')

    # Registration status
    TESTING = 'TG'
    ACCEPTED = 'AC'
    TESTING_FAILED = 'TF'
    ENROLLED = 'ER'
    ISSUED = 'IS'
    STUDYING = 'ST'
    SUCCESSED = 'SC'
    FAILED = 'FL'
    DISQUALIFIED = 'DQ'

    EVENT_APPLICATION_STATUS_CHOICES = (
        (TESTING, _('Testing')),
        (ACCEPTED, _('Accepted')),
        (TESTING_FAILED, _('Testing failed')),
        (ENROLLED, _('Enrolled')),
        (ISSUED, _('Issued')),
        (STUDYING, _('Studying')),
        (SUCCESSED, _('Successed')),
        (FAILED, _('Failed')),
        (DISQUALIFIED, _('Disqualified'))
    )

    ENROLLED_STATUSES = (
        # ACCEPTED, TODO: Determine if we need to show ACCEPTED in enrolled table
        ENROLLED,
        ISSUED,
        STUDYING,
        SUCCESSED,
        FAILED,
        DISQUALIFIED
    )

    status = models.CharField(max_length=2, choices=EVENT_APPLICATION_STATUS_CHOICES,
                              default=TESTING, verbose_name=_('Application status'))

    def __str__(self):
        return self.user.get_full_name() + " - " + self.event.__str__()

    def __init__(self, *args, **kwargs):
        super(EventApplication, self).__init__(*args, **kwargs)
        self.__original_status = self.status

    @property
    def enrolled_color(self):
        if self.status in (EventApplication.FAILED, EventApplication.DISQUALIFIED):
            return 'danger'
        if self.status == EventApplication.ENROLLED:
            return 'warning'
        if self.status in EventApplication.ENROLLED_STATUSES:
            return 'success'
        return 'danger'

    def save(self, *args, **kwargs):
        from userprofile.models import Relationship
        try:
            from telegram.bot import HOST
        except ImportError:
            HOST = ''

        def notify(msg, id=None):
            from telegram.bot import TelegramBot
            id = id or self.user.telegram_id
            if id is not None:
                TelegramBot.sendMessage(id, msg, parse_mode="Markdown")

        if self.status != EventApplication.TESTING and self.submitted_at is None:
            self.submitted_at = timezone.now()
        if self.status == EventApplication.ISSUED and self.issued_at is None:
            self.issued_at = timezone.now()
        if self.status != self.__original_status:

            if self.status == EventApplication.ENROLLED:
                # notify student
                notify('''
*Поздравляем!*
Вы зачислены в группу {group}. Теперь необходимо оплатить путёвку.
[Страница заявки]({link})
'''.format(group=self.event.name,
           link=HOST + reverse('applications_group_application', args=[self.id])))

                # notify parents
                for rel in Relationship.objects.filter(child=self.user, request=Relationship.APPROVED)\
                        .exclude(relative__telegram_id__isnull=True):
                    notify('''
*Поздравляем!*
{child} зачислен(а) в {group}. Теперь необходимо оплатить путёвку.
[Страница заявки]({link})
'''.format(group=self.event.name, child=self.user.get_full_name(),
           link=HOST + reverse('applications_group_application', args=[self.id])), rel.relative.telegram_id)

            if self.status == EventApplication.ISSUED:
                # notify student
                notify('''
*Путёвка одобрена*
Ваша путёвка в {period} была одобрена.
[Страница заявки]({link})
'''.format(period=self.event.period.name,
           link=HOST + reverse('applications_group_application', args=[self.id])))

                # notify parents
                for rel in Relationship.objects.filter(child=self.user, request=Relationship.APPROVED)\
                        .exclude(relative__telegram_id__isnull=True):
                    notify('''
*Путёвка одобрена*
{child}: Путёвка в {period} была одобрена.
[Страница заявки]({link})
'''.format(period=self.event.period.name, child=self.user.get_full_name(),
           link=HOST + reverse('applications_group_application', args=[self.id])), rel.relative.telegram_id)

        super(EventApplication, self).save(*args, **kwargs)

    @property
    def is_general_filled(self):
        return self.grade is not None and \
               self.address is not None and \
               self.school is not None and \
               self.personal_data_doc is not None

    @property
    def modifiable(self):
        return self.status == EventApplication.TESTING

    def has_parent_privileges(self, user):
        if user.is_staff:
            return True
        from userprofile.models import Relationship
        return Relationship.objects.filter(relative=user, child=self.user, request=Relationship.APPROVED).exists()

    def has_child_privileges(self, user):
        if user.is_staff:
            return True
        return user == self.user

    def has_global_privileges(self, user):
        if user.is_superuser:
            return True
        if user.is_education_committee:
            return True
        return False

    def viewable(self, user):
        return self.has_global_privileges(user) or self.has_parent_privileges(user) or self.has_child_privileges(user)