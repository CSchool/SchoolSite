import tempfile
import os

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views.decorators.http import require_POST

from applications.forms import CreateApplicationForm, EventApplicationGenericForm, TextDisplayWidget, \
    EventApplicationRenderForm, EventApplicationPrivForm, EventApplicationVoucherForm
from applications.models import Period, Event, PracticeExamApplication, EventApplication, PracticeExamRun, \
    TheoryExamApplication, TheoryExamApplicationQuestion, TheoryExamQuestion, PracticeExamProblem, PeriodAttachment
from applications.decorators import study_group_application
from userprofile.models import Relationship, User
from main.helpers import file_response, get_sapp
import ejudge


def view_enrolled(req, period_id):
    try:
        period = Period.objects.get(id=period_id)
    except Period.DoesNotExist:
        raise Http404
    applications = EventApplication.objects\
        .filter(event__period=period)\
        .filter(event__type=Event.CLASS_GROUP)\
        .filter(status__in=EventApplication.ENROLLED_STATUSES)
    if req.user.is_authenticated and req.user.is_education_committee:
        applications = applications.order_by('user__last_name', 'user__first_name')
    else:
        applications = applications.order_by('event__difficulty', 'user__last_name', 'user__first_name')
    return render(req, "applications/view_enrolled.html", {
        "period": period,
        "applications": applications,
        "sapp": get_sapp(req)
    })


def choose_period(req):
    periods = []
    pmap = {}
    if req.user.is_authenticated and req.user.is_eligible_for_application_viewing():
        for p in Period.objects.order_by("-begin").all():
            status, status_verbose, app_id = p.get_application_status(req.user) # TODO: N + 1 query is bad
            pmap[p.id] = len(periods)
            periods.append(dict(period=p, status=status, status_verbose=status_verbose, app_id=app_id,
                                allow=req.user.is_eligible_for_application(p), achildren=[]))
        if req.user.is_eligible_for_application():
            children = Relationship.objects.filter(relative=req.user, request=Relationship.APPROVED).all()
            assoc = EventApplication.objects\
                .filter(user_id__in=map(lambda x: x.child.id, children))\
                .filter(event__type=Event.CLASS_GROUP)\
                .filter(event__period_id__in=map(lambda x: x['period'].id, periods))\
                .all()
            for ea in assoc:
                periods[pmap[ea.event.period.id]]['achildren'].append(dict(child=ea.user, application=ea))
            for p in periods:
                p['achildren_set'] = set([x['child'].id for x in p['achildren']])
            children_set = set(children)
            for p in periods:
                p['children'] = []
                for child in children_set:
                    if child.child.id not in p['achildren_set']:
                        p['children'].append(child.child)
    else:
        for p in Period.objects.order_by("-begin").all():
            periods.append(dict(period=p, status="NA", status_verbose="Not applicable", allow=False))

    return render(req, "applications/choose_period.html", {
        "periods": periods
    })


@login_required
@study_group_application
def choose_group(req, user_id, period_id):
    try:
        period = Period.objects.get(id=period_id)
        user = User.objects.get(id=user_id)
    except Exception:
        raise Http404
    if not req.user.is_eligible_for_application(period):
        raise PermissionDenied
    if not Relationship.objects.filter(relative=req.user, child=user, request=Relationship.APPROVED).exists():
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
        "move": False,
        "username": user.username
    })


@login_required
def move_group(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        if not application.viewable(req.user):
            raise PermissionDenied
        if not application.has_parent_privileges(req.user):
            raise PermissionDenied
        group = application.event
        period = group.period
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
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
        "move": move,
        "application": application,
        "username": application.user
    })


@login_required
@require_POST
def create_application(req):
    form = CreateApplicationForm(req.POST)
    if form.is_valid():
        try:
            group = Event.objects.get(id=form.cleaned_data['group_id'], type=Event.CLASS_GROUP)
            user = User.objects.get(username=form.cleaned_data['username'])
            period = group.period
        except Exception:
            raise PermissionDenied
        if not req.user.is_eligible_for_application(group.period):
            raise PermissionDenied
        if not Relationship.objects.filter(relative=req.user, child=user, request=Relationship.APPROVED).exists():
            raise PermissionDenied
        if req.POST.get('move'):
            # move application
            try:
                ea = EventApplication.objects.filter(event__period=period, user=user, event__type=Event.CLASS_GROUP).get()
            except EventApplication.DoesNotExist:
                raise PermissionDenied
            if hasattr(ea, 'theory_exam') and ea.theory_exam:
                ea.theory_exam.delete()
            if hasattr(ea, 'practice_exam') and ea.practice_exam:
                ea.practice_exam.delete()
            ea.status = EventApplication.TESTING
            ea.issued_by = None
            ea.issued_at = None
            ea.submitted_at = None
            ea.user = user
            ea.event = group
            ea.save()
        else:
            try:
                ea = EventApplication.objects.get(user=user, event=group)
            except EventApplication.DoesNotExist:
                ea = EventApplication.objects.create(user=user, event=group)
            ea.voucher_parent = req.user.get_initials()
            if req.user.phone:
                ea.parent_phone_numbers = "{} - {}".format(req.user.get_initials(), req.user.phone)
            ea.save()
        if hasattr(group, 'practiceexam'):
            PracticeExamApplication.generate_for_user(user, group.practiceexam).save()
        if hasattr(group, 'theoryexam'):
            TheoryExamApplication.generate_for_user(user, group.theoryexam).save()
        return redirect(reverse('applications_group_application', args=[ea.id]))
    raise PermissionDenied

@login_required
def group_application_edu(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        group = application.event
    except EventApplication.DoesNotExist:
        raise Http404
    if not application.has_global_privileges(req.user):
        raise PermissionDenied
    if req.method == "POST":
        form = EventApplicationVoucherForm(req.POST, instance=application)
        if form.is_valid():
            application.voucher_id = form.cleaned_data['voucher_id']
            application.status = EventApplication.ISSUED
            application.issued_by = req.user
            application.save()
            return redirect(reverse('applications_view_enrolled', args=[group.period.id]))
    else:
        form = EventApplicationPrivForm(instance=application)
    for key in form.fields.keys():
        if key != "voucher_id":
            form.fields[key].widget = TextDisplayWidget()
            form.fields[key].help_text = None

    return render(req, "applications/group_application_voucher.html", {
        "form": form,
        "application": application,
        "group": group,
        "personal_data_doc_name": os.path.basename(application.personal_data_doc.name)
    })


@login_required
def group_application(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        if not application.viewable(req.user):
            raise PermissionDenied
        group = application.event
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

    parent_priv = application.has_parent_privileges(req.user)
    child_priv = application.has_child_privileges(req.user)
    priv = application.has_global_privileges(req.user)
    confirm_submit = False

    if req.POST.get('confirm_submit') is not None or 'c' in req.GET:
        if application.modifiable and application.is_general_filled:
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
            application.status = EventApplication.ACCEPTED
        else:
            application.status = EventApplication.TESTING_FAILED
        application.save()
        return redirect(reverse('applications_group_application', args=[application.id]))

    info_form = EventApplicationGenericForm(instance=application)
    for key in info_form.fields.keys():
        info_form.fields[key].widget = TextDisplayWidget()
        info_form.fields[key].help_text = None

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

    submit_priv = application.modifiable and not confirm_submit
    if parent_priv and application.testing_required:
        submit_priv = False

    delete_priv = application.has_delete_privileges(req.user) and not confirm_submit

    return render(req, "applications/group_application.html", {
        "group": group,
        "application": application,
        "solved_practice": practice_solved,
        "total_practice": practice_total,
        "answered_theory": theory_answered,
        "total_theory": theory_total,
        "info_form": info_form,
        "confirm_submit": confirm_submit,
        "parent_priv": parent_priv,
        "child_priv": child_priv,
        "priv": priv,
        "personal_data_doc_name": os.path.basename(application.personal_data_doc.name),
        "attachments": PeriodAttachment.objects.filter(period=group.period).order_by('id').all(),
        "submit_priv": submit_priv,
        "delete_priv": delete_priv
    })


@login_required
def group_application_edit_info(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        if not application.viewable(req.user):
            raise PermissionDenied
        group = application.event
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
    uploaded = None
    render_file = False
    parent_priv = application.has_parent_privileges(req.user)
    if req.method == "POST":
        if not application.modifiable or not parent_priv:
            raise PermissionDenied
        form = EventApplicationGenericForm(req.POST, req.FILES, instance=application)
        if form.is_valid():
            # form.save() # We handle file upload separately, because privacy
            form = EventApplicationRenderForm(req.POST, instance=application)
            if form.is_valid():
                doc = req.FILES.get('personal_data_doc')
                if doc is not None:
                    path = os.path.join('personal_data_docs', 'user_%d' % application.user_id, doc.name)
                    application.personal_data_doc.name = path
                form.save()
                application.save()
                if not application.testing_required:
                    # Redirect parent straight to confirm everything page
                    return redirect(reverse('applications_group_application', args=[application.id]) + '?c')
                return redirect(reverse('applications_group_application', args=[application.id]))
            else:
                render_file = True # But why would it be invalid
    else:
        form = EventApplicationRenderForm(instance=application)
        render_file = True
        uploaded = os.path.basename(application.personal_data_doc.name)
        if not application.modifiable:
            for key in form.fields.keys():
                form.fields[key].widget = TextDisplayWidget()
                form.fields[key].help_text = None
    personal_data_attachments = PeriodAttachment.objects.filter(period=group.period,
                                                               type=PeriodAttachment.AGREEMENT).all()
    return render(req, "applications/group_application_edit_info.html", {
        "group": group,
        "application": application,
        "form": form,
        "uploaded": uploaded,
        "render_file": render_file,
        "personal_data_attachments": personal_data_attachments
    })


@login_required
def group_application_view_statement(req, application_id, problem_id, filename):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        if not application.viewable(req.user):
            raise PermissionDenied
        group = application.event
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
    if filename != os.path.basename(problem.statement.name):
        raise Http404
    return file_response(problem.statement)


def period_download_attachment(req, attachment_id, filename):
    try:
        attachment = PeriodAttachment.objects.get(id=attachment_id)
    except PeriodAttachment.DoesNotExist:
        raise Http404
    if os.path.basename(attachment.file.name) != filename:
        raise Http404
    response = file_response(attachment.file)
    response['Content-Disposition'] = 'attachment'
    return response


@login_required
def group_application_doc(req, application_id, filename):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        if not application.viewable(req.user):
            raise PermissionDenied
        group = application.event
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
    if not application.personal_data_doc:
        raise Http404
    if os.path.basename(application.personal_data_doc.name) != filename:
        raise Http404
    return file_response(application.personal_data_doc)



@login_required
def group_application_practice_exam(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        if not application.viewable(req.user):
            raise PermissionDenied
        group = application.event
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
    if application.practice_exam is None:
        raise Http404
    child_priv = application.has_child_privileges(req.user)
    problems = []
    all_runs = PracticeExamRun.objects.filter(problem__in=application.practice_exam.problems.all(), user=application.user) \
        .order_by('-submitted').all()
    for problem in application.practice_exam.problems.all():
        problems.append({
            "problem": problem,
            "runs": all_runs.filter(problem=problem),
            "statement_url": reverse('applications_view_statement',
                                     args=[application.id, problem.id, os.path.basename(problem.statement.name)])
        })
    return render(req, "applications/group_application_practice_exam.html", {
        "group": group,
        "application": application,
        "problems": problems,
        "child_priv": child_priv,
    })


@login_required
def group_application_theory_exam(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        if not application.viewable(req.user):
            raise PermissionDenied
        group = application.event
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
    if application.theory_exam is None:
        raise Http404
    child_priv = application.has_child_privileges(req.user)
    questions = list(TheoryExamApplicationQuestion.objects.filter(application=application.theory_exam).all())
    qs = []
    qsbm = {}
    for question in questions:
        empty = False
        form = question.django_form
        if form is None:
            empty = True
            form = question.question.django_form()
        if not application.modifiable or not child_priv:
            for key in form.fields.keys():
                form.fields[key].widget = TextDisplayWidget()
                form.fields[key].help_text = None
        qs.append({
            "question": question,
            "form": form,
            "display": not empty or (application.modifiable and child_priv)
        })
        qsbm[question.question.id] = len(qs) - 1
    if req.POST.get('qsubmit'):
        if not application.modifiable or not child_priv:
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
                return redirect(reverse('applications_group_application_theory_exam', args=[application.id]) + "#q" + str(
                    question.question.id))
            else:
                qs[qsbm[question.question.id]]['form'] = form
        except:
            raise PermissionDenied

    return render(req, "applications/group_application_theory_exam.html", {
        "group": group,
        "application": application,
        "questions": qs,
        "child_priv": child_priv,
    })


@login_required
@require_POST
def group_application_submit_run(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        if not application.viewable(req.user):
            raise PermissionDenied
        group = application.event
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
        return redirect(reverse('applications_group_application_practice_exam', args=[application.id]))
    except:
        raise PermissionDenied


@login_required
def group_application_delete_confirmation(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        if not application.viewable(req.user):
            raise PermissionDenied
        group = application.event
    except EventApplication.DoesNotExist:
        raise Http404
    if not application.has_delete_privileges(req.user):
        raise PermissionDenied
    return render(req, "applications/confirm_application_delete.html", {
        "application": application,
        "group": application.event,
        "period": application.event.period
    })


@login_required
@require_POST
def group_application_delete(req, application_id):
    try:
        application = EventApplication.objects.get(id=application_id, event__type=Event.CLASS_GROUP)
        if not application.viewable(req.user):
            raise PermissionDenied
        group = application.event
    except EventApplication.DoesNotExist:
        raise Http404
    if not application.has_delete_privileges(req.user):
        raise PermissionDenied
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
