import tempfile

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views.decorators.http import require_POST

from applications.forms import CreateApplicationForm, EventApplicationGenericForm
from applications.models import Period, Event, PracticeExamApplication, EventApplication, PracticeExamRun, \
    TheoryExamApplication, TheoryExamApplicationQuestion, TheoryExamQuestion
from applications.decorators import study_group_application
import ejudge


@login_required
def choose_period(req):
    if not req.user.is_eligible_for_application():
        raise PermissionDenied
    periods = Period.objects.all().order_by("-begin")
    return render(req, "applications/choose_period.html", {
        "periods": periods
    })


@login_required
@study_group_application
def choose_group(req, period_id):
    try:
        period = Period.objects.get(id=period_id)
    except Period.DoesNotExist:
        raise Http404
    if not req.user.is_eligible_for_application(period):
        raise PermissionDenied
    groups = period.event_set.filter(type=Event.CLASS_GROUP).all()
    metatypes = {}
    for group in groups:
        if group.metatype not in metatypes:
            metatypes[group.metatype] = dict(groups=[], colwidth=12, name=group.metatype)
        metatypes[group.metatype]['groups'].append(group)
        metatypes[group.metatype]['colwidth'] = 12 // len(metatypes[group.metatype]['groups'])
    return render(req, "applications/choose_group.html", {
        "period": period,
        "metatypes": list(metatypes.values())
    })


@login_required
@study_group_application
def confirm_group(req, group_id):
    try:
        group = Event.objects.get(id=group_id, type=Event.CLASS_GROUP)
    except Event.DoesNotExist:
        raise Http404
    period = group.period
    if not req.user.is_eligible_for_application(period):
        raise PermissionDenied
    return render(req, "applications/confirm_group.html", {
        "period": period,
        "group": group
    })


@login_required
@require_POST
def create_application(req):
    form = CreateApplicationForm(req.POST)
    if form.is_valid():
        try:
            group = Event.objects.get(id=form.cleaned_data['group_id'], type=Event.CLASS_GROUP)
        except Event.DoesNotExist:
            raise PermissionDenied
        if not req.user.is_eligible_for_application(group.period):
            raise PermissionDenied
        try:
            ea = EventApplication.objects.get(user=req.user, event=group)
        except EventApplication.DoesNotExist:
            ea = EventApplication.objects.create(user=req.user, event=group)
            ea.save()
        if hasattr(group, 'practiceexam'):
            PracticeExamApplication.generate_for_user(req.user, group.practiceexam).save()
        if hasattr(group, 'theoryexam'):
            TheoryExamApplication.generate_for_user(req.user, group.theoryexam).save()
        return redirect(reverse('applications_group_application', args=[group.id]))
    raise PermissionDenied


@login_required
def group_application(req, group_id):
    try:
        group = Event.objects.get(id=group_id, type=Event.CLASS_GROUP, eventapplication__user=req.user)
        application = group.eventapplication_set.get(user=req.user)
        try:
            practice_exam = application.practice_exam
        except PracticeExamApplication.DoesNotExist:
            practice_exam = None

        try:
            theory_exam = application.theory_exam
        except TheoryExamApplication.DoesNotExist:
            theory_exam = None
    except:
        raise Http404

    if practice_exam is None:
        practice_solved = None
        practice_total = None
    else:
        practice_solved = practice_exam.solved_problems
        practice_total = practice_exam.total_problems

    if theory_exam is None:
        theory_answered = None
        theory_total = None
    else:
        theory_answered = theory_exam.answered_questions
        theory_total = theory_exam.total_questions

    return render(req, "applications/group_application.html", {
        "group": group,
        "application": application,
        "solved_practice": practice_solved,
        "total_practice": practice_total,
        "answered_theory": theory_answered,
        "total_theory": theory_total
    })


@login_required
def group_application_edit_info(req, group_id):
    try:
        group = Event.objects.get(id=group_id, type=Event.CLASS_GROUP, eventapplication__user=req.user)
        application = group.eventapplication_set.get(user=req.user)
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
    if req.method == "POST":
        form = EventApplicationGenericForm(req.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect(reverse('applications_group_application', args=[group_id]))
    else:
        form = EventApplicationGenericForm(instance=application)
    return render(req, "applications/group_application_edit_info.html", {
        "group": group,
        "application": application,
        "form": form
    })


@login_required
def group_application_practice_exam(req, group_id):
    try:
        group = Event.objects.get(id=group_id, type=Event.CLASS_GROUP, eventapplication__user=req.user)
        application = group.eventapplication_set.get(user=req.user)
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
    if application.practice_exam is None:
        raise Http404
    problems = []
    all_runs = PracticeExamRun.objects.filter(problem__in=application.practice_exam.problems.all(), user=req.user) \
        .order_by('-submitted').all()
    for problem in application.practice_exam.problems.all():
        problems.append({
            "problem": problem,
            "runs": all_runs.filter(problem=problem)
        })
    return render(req, "applications/group_application_practice_exam.html", {
        "group": group,
        "application": application,
        "problems": problems
    })


@login_required
def group_application_theory_exam(req, group_id):
    try:
        group = Event.objects.get(id=group_id, type=Event.CLASS_GROUP, eventapplication__user=req.user)
        application = group.eventapplication_set.get(user=req.user)
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
    if application.theory_exam is None:
        raise Http404
    questions = list(TheoryExamApplicationQuestion.objects.filter(application=application.theory_exam).all())
    qs = []
    qsbm = {}
    for question in questions:
        qs.append({
            "question": question,
            "form": question.django_form
        })
        qsbm[question.question.id] = len(qs) - 1
    if req.POST.get('qsubmit'):
        try:
            question = TheoryExamApplicationQuestion.objects.get(id=int(req.POST['question_id']))
            form = question.question.django_form(req.POST)
            if form.is_valid():
                picked = form.cleaned_data.get('answer')
                if question.question.qtype == TheoryExamQuestion.MULTICHOICE:
                    question.answer = ','.join(sorted(picked))
                else:
                    question.answer = picked
                question.save()
                return redirect(reverse('applications_group_application_theory_exam', args=[group_id]) + "#q" + str(
                    question.question.id))
            else:
                qs[qsbm[question.question.id]]['form'] = form
        except:
            raise PermissionDenied

    return render(req, "applications/group_application_theory_exam.html", {
        "group": group,
        "application": application,
        "questions": qs
    })


@login_required
@require_POST
def group_application_submit_run(req, group_id):
    try:
        group = Event.objects.get(id=group_id, type=Event.CLASS_GROUP, eventapplication__user=req.user)
        application = group.eventapplication_set.get(user=req.user)
        if 'source' not in req.FILES:
            raise PermissionDenied
        if 'lang' not in req.POST:
            raise PermissionDenied
        if 'problem_id' not in req.POST:
            raise PermissionDenied
        file = req.FILES['source']
        with tempfile.NamedTemporaryFile() as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
                tmp.flush()
            PracticeExamRun.submit(req, req.POST['problem_id'], req.POST['lang'], tmp.name)
        return redirect(reverse('applications_group_application_practice_exam', args=[group_id]))
    except:
        raise PermissionDenied


@login_required
@require_POST
def group_application_delete(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, user=req.user)
    except EventApplication.DoesNotExist:
        raise Http404
    application.delete()
    return redirect(reverse('index'))


@login_required
def download_run(req, run_id):
    try:
        run = PracticeExamRun.objects.get(id=run_id, user=req.user)
    except PracticeExamRun.DoesNotExist:
        raise Http404
    res = HttpResponse(ejudge.get_run_source(run.ejudge_run_id), content_type="text/plain")
    return res


@login_required
def run_log(req, run_id):
    try:
        run = PracticeExamRun.objects.get(id=run_id, user=req.user)
    except PracticeExamRun.DoesNotExist:
        raise Http404
    res = run.compile_log
    if res is None:
        raise Http404
    return HttpResponse(res, content_type='text/plain')