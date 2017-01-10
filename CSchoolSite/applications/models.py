from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import ejudge


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
        return False


class CampVoucher(models.Model):
    class Meta:
        verbose_name = _('Camp voucher')
        verbose_name_plural = _('Camp vouchers')
        permissions = (
            ("view_campvoucher", _("view camp vouchers")),
        )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Voucher owner'))
    period = models.ForeignKey('Period', on_delete=models.CASCADE, verbose_name=_('Period'))
    voucher_id = models.CharField(max_length=30, verbose_name=_('Voucher ID'))

    # Voucher status
    AWAITING_PAYMENT = 'WP'
    DECLINED = 'DC'
    PAID = 'PD'
    APPROVED = 'AP'

    CAMP_VOUCHER_STATUS_CHOICES = (
        (AWAITING_PAYMENT, _('Awaiting payment')),
        (DECLINED, _('Declined')),
        (PAID, _('Paid')),
        (APPROVED, _('Approved'))
    )

    status = models.CharField(max_length=2, choices=CAMP_VOUCHER_STATUS_CHOICES, default=AWAITING_PAYMENT, verbose_name='Статус')

    def __str__(self):
        return self.voucher_id


class Event(models.Model):
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    period = models.ForeignKey('Period', on_delete=models.CASCADE, verbose_name=_('Period'))
    users = models.ManyToManyField(User, through='EventApplication')
    description = models.TextField(verbose_name=_('Description'))
    begin = models.DateTimeField(verbose_name=_('Event begins'))
    end = models.DateTimeField(verbose_name=_('Event ends'))
    registration_begin = models.DateTimeField(verbose_name=_('Registration begins'))
    registration_end = models.DateTimeField(verbose_name=_('Registration ends'))
    is_open = models.BooleanField(verbose_name=_('Registration open'))
    limit = models.IntegerField(verbose_name=_('Participants limit'))

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
        return self.name

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
        return self.event.name


class PracticeExamProblem(models.Model):
    class Meta:
        verbose_name = _('Practice exam problem')
        verbose_name_plural = _('Practice exams problems')
    name = models.CharField(max_length=250, verbose_name=_('Problem name'))
    ejudge_id = models.CharField(max_length=100, verbose_name=_('Problem id'), unique=True)
    slot = models.IntegerField(verbose_name=_('Problem slot'))
    statement_url = models.CharField(max_length=500, verbose_name=_('Statement URL'))
    score = models.IntegerField(verbose_name=_('Problem score'))

    exam = models.ForeignKey(PracticeExam)

    def __str__(self):
        return self.name


class PracticeExamRun(models.Model):
    class Meta:
        verbose_name = _('Practice exam run')
        verbose_name_plural = ('Practice exams runs')
    user = models.ForeignKey(User)
    ejudge_run_id = models.IntegerField(verbose_name=_('Run ID'), unique=True)
    problem = models.ForeignKey(PracticeExamProblem)

    @property
    def info(self):
        return ejudge.get_run_info(self.ejudge_run_id)

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
    user = models.ForeignKey(User)
    problems = models.ManyToManyField(PracticeExamProblem, through='PracticeExamApplicationProblem')

    @staticmethod
    def generate_for_user(user, practice_exam):
        try:
            application = EventApplication.objects.get(user=user, event=practice_exam.event)
        except EventApplication.DoesNotExist:
            application = EventApplication()
            application.user = user
            application.event = practice_exam.event
        exam_application = PracticeExamApplication()
        exam_application.user = user
        exam_application.eventapplication = application
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
        for rng in range(practice_exam.rand_problems):
            try:
                problems = PracticeExamProblem.objects.filter(exam=practice_exam, slot=slot).all()
            except PracticeExamProblem.DoesNotExist:
                continue
            if len(problems) > 0:
                from random import randint
                problem = problems[randint(0, len(problems) - 1)]
                a_problem = PracticeExamApplicationProblem()
                a_problem.problem = problem
                a_problem.index = rng + practice_exam.slot_problems + 1
                a_problem.application = exam_application
                a_problem.save()
        return exam_application


class PracticeExamApplicationProblem(models.Model):
    # TODO: Should it be visible in admin panel?
    class Meta:
        ordering = ('index',)
    application = models.ForeignKey(PracticeExamApplication)
    problem = models.ForeignKey(PracticeExamProblem)
    index = models.IntegerField()


class EventApplication(models.Model):
    class Meta:
        verbose_name = _('Event application')
        verbose_name_plural = _('Event applications')
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    practice_exam = models.ForeignKey(PracticeExamApplication)

    # Registration status
    TESTING = 'TG'
    TESTING_SUCCEEDED = 'TS'
    STUDYING = 'ST'
    SUCCESSED = 'SC'
    FAILED = 'FL'
    DISQUALIFIED = 'DQ'

    EVENT_APPLICATION_STATUS_CHOICES = (
        (TESTING, _('Testing')),
        (TESTING_SUCCEEDED, _('Testing succeeded')),
        (STUDYING, _('Studying')),
        (SUCCESSED, _('Successed')),
        (FAILED, _('Failed')),
        (DISQUALIFIED, _('Disqualified'))
    )

    status = models.CharField(max_length=2, choices=EVENT_APPLICATION_STATUS_CHOICES, default=TESTING, verbose_name=_('Application status'))

