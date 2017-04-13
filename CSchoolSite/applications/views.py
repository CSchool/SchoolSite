import tempfile
import mimetypes

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views.decorators.http import require_POST

from applications.forms import CreateApplicationForm, EventApplicationGenericForm, TextDisplayWidget, VoucherForm
from applications.models import Period, Event, PracticeExamApplication, EventApplication, PracticeExamRun, \
    TheoryExamApplication, TheoryExamApplicationQuestion, TheoryExamQuestion, PracticeExamProblem, CampVoucher
from applications.decorators import study_group_application
import ejudge


@login_required
def choose_period(req):
    if not req.user.is_eligible_for_application():
        raise PermissionDenied
    periods = []
    for p in Period.objects.order_by("-begin").all():
        status, status_verbose = p.get_application_status(req.user)
        periods.append(dict(period=p, status=status, status_verbose=status_verbose))
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
    groups = period.event_set.filter(type=Event.CLASS_GROUP).order_by("difficulty").all()
    categories = {}
    for group in groups:
        if group.category not in categories:
            categories[group.category] = dict(groups=[], colwidth=12, name=group.category)
        categories[group.category]['groups'].append(group)
        categories[group.category]['colwidth'] = 12 // len(categories[group.category]['groups'])
    return render(req, "applications/choose_group.html", {
        "period": period,
        "categories": sorted(list(categories.values()), key=lambda x: x['name']),
        "move": False
    })


@login_required
def move_group(req, period_id):
    try:
        period = Period.objects.get(id=period_id)
        application = EventApplication.objects.filter(event__period=period, user=req.user).get()
    except Period.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise PermissionDenied
    if not req.user.is_eligible_for_application(period):
        raise PermissionDenied
    move = True
    groups = period.event_set.filter(type=Event.CLASS_GROUP, category=application.event.category)\
        .filter(difficulty__lt=application.event.difficulty).order_by("difficulty").all()
    if not groups:
        groups = period.event_set.filter(type=Event.CLASS_GROUP).order_by("difficulty").all()
        move = False
    categories = {}
    for group in groups:
        if group.category not in categories:
            categories[group.category] = dict(groups=[], colwidth=12, name=group.category)
        categories[group.category]['groups'].append(group)
        categories[group.category]['colwidth'] = 12 // len(categories[group.category]['groups'])
    return render(req, "applications/choose_group.html", {
        "period": period,
        "categories": sorted(list(categories.values()), key=lambda x: x['name']),
        "move": move
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
            period = group.period
        except Event.DoesNotExist:
            raise PermissionDenied
        if not req.user.is_eligible_for_application(group.period):
            raise PermissionDenied
        if req.POST.get('move'):
            # move application
            try:
                ea = EventApplication.objects.filter(event__period=period, user=req.user).get()
            except EventApplication.DoesNotExist:
                raise PermissionDenied
            if hasattr(ea, 'theory_exam') and ea.theory_exam:
                ea.theory_exam.delete()
            if hasattr(ea, 'practice_exam') and ea.practice_exam:
                ea.practice_exam.delete()
            ea.status = EventApplication.TESTING
            ea.user = req.user
            ea.event = group
            ea.save()
        else:
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

    confirm_submit = False
    if req.POST.get('confirm_submit') is not None:
        if application.modifiable:
            confirm_submit = True

    if req.POST.get('confirm_application_submit') is not None:
        if not application.modifiable:
            raise PermissionDenied
        if not application.is_general_filled:
            raise PermissionDenied
        passed = True
        if theory_exam:
            passed = passed and theory_exam.passed
        if practice_exam:
            passed = passed and practice_exam.passed
        if passed:
            application.status = EventApplication.TESTING_SUCCEEDED
        else:
            application.status = EventApplication.TESTING_FAILED
        application.save()
        return redirect(reverse('applications_group_application', args=[group_id]))

    try:
        voucher = CampVoucher.objects.filter(user=req.user, period=group.period).get()
    except CampVoucher.DoesNotExist:
        voucher = None

    if req.POST.get('voucher_submit'):
        voucher_form = VoucherForm(req.POST)
        if voucher_form.is_valid():
            application.confirm_participation = voucher_form.cleaned_data.get('confirm_participation')
            application.save()
            if voucher_form.cleaned_data.get('voucher_id'):
                if not voucher:
                    voucher = CampVoucher.objects.create(user=req.user,
                                                         period=group.period,
                                                         voucher_id=voucher_form.cleaned_data.get('voucher_id'),
                                                         status=CampVoucher.AWAITING_PAYMENT)
                else:
                    if voucher.voucher_id != voucher_form.cleaned_data.get('voucher_id'):
                        voucher.voucher_id = voucher_form.cleaned_data.get('voucher_id')
                        voucher.status = CampVoucher.AWAITING_PAYMENT
                voucher.save()
            else:
                if voucher:
                    voucher.delete()
            return redirect(reverse('applications_group_application', args=[group.id]))
    else:
        voucher_form = VoucherForm()
        if voucher:
            voucher_form.fields['voucher_id'].initial = voucher.voucher_id
        voucher_form.fields['confirm_participation'].initial = application.confirm_participation

    form = EventApplicationGenericForm(instance=application)
    for key in form.fields.keys():
        form.fields[key].widget = TextDisplayWidget()
        form.fields[key].help_text = None

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
        "total_theory": theory_total,
        "info_form": form,
        "confirm_submit": confirm_submit,
        "voucher": voucher,
        "voucher_form": voucher_form
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
        if not application.modifiable:
            raise PermissionDenied
        form = EventApplicationGenericForm(req.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect(reverse('applications_group_application', args=[group_id]))
    else:
        form = EventApplicationGenericForm(instance=application)
        if not application.modifiable:
            for key in form.fields.keys():
                form.fields[key].widget = TextDisplayWidget()
                form.fields[key].help_text = None
    return render(req, "applications/group_application_edit_info.html", {
        "group": group,
        "application": application,
        "form": form
    })


@login_required
def group_application_voucher_info(req, group_id):
    try:
        group = Event.objects.get(id=group_id, type=Event.CLASS_GROUP, eventapplication__user=req.user)
        application = group.eventapplication_set.get(user=req.user)
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
    if application.status != EventApplication.TESTING_SUCCEEDED:
        raise PermissionDenied
    if req.method == "POST":
        form = VoucherForm(req.POST)
    else:
        form = VoucherForm()
        try:
            voucher = CampVoucher.objects.get(period=group.period, user=req.user)
            form.fields['voucher_id'].initial = voucher.voucher_id
        except CampVoucher.DoesNotExist:
            voucher = None
        form.fields['confirm_participation'].initial = application.confirm_participation
    return render(req, "applications/group_application_edit_info.html", {
        "group": group,
        "application": application,
        "form": form
    })


@login_required
def group_application_view_statement(req, group_id, problem_id):
    try:
        group = Event.objects.get(id=group_id, type=Event.CLASS_GROUP, eventapplication__user=req.user)
        application = group.eventapplication_set.get(user=req.user)
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
    if application.practice_exam is None:
        raise Http404
    try:
        problem = application.practice_exam.problems.filter(id=problem_id).get()
    except PracticeExamProblem.DoesNotExist:
        raise Http404
    if problem.statement is None:
        raise Http404
    mime = mimetypes.MimeTypes()
    mime_type = mime.guess_type(problem.statement.path)[0]
    f = problem.statement.file
    f.open()
    content = f.read()
    f.close()
    return HttpResponse(content, content_type=mime_type)


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
            "runs": all_runs.filter(problem=problem),
            "statement_url": reverse('applications_view_statement', args=[group.id, problem.id])
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
        empty = False
        form = question.django_form
        if form is None:
            empty = True
            form = question.question.django_form()
        if not application.modifiable:
            for key in form.fields.keys():
                form.fields[key].widget = TextDisplayWidget()
                form.fields[key].help_text = None
        qs.append({
            "question": question,
            "form": form,
            "display": not empty or application.modifiable
        })
        qsbm[question.question.id] = len(qs) - 1
    if req.POST.get('qsubmit'):
        if not application.modifiable:
            raise PermissionDenied
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
        if not application.modifiable:
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
def group_application_delete_confirmation(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, user=req.user)
    except EventApplication.DoesNotExist:
        raise Http404
    return render(req, "applications/confirm_application_delete.html", {
        "application": application,
        "group": application.event,
        "period": application.event.period
    })


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