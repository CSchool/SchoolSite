from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import render, redirect, reverse
from django.views.decorators.http import require_POST

from applications.forms import CreateApplication, EventApplicationGeneric
from applications.models import Period, Event, PracticeExamApplication, EventApplication
from applications.decorators import study_group_application


@login_required
def choose_period(req):
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
    groups = Event.objects.all().filter(type=Event.CLASS_GROUP)
    return render(req, "applications/choose_group.html", {
        "period": period,
        "groups": groups
    })


@login_required
@study_group_application
def confirm_group(req, group_id):
    try:
        group = Event.objects.get(id=group_id, type=Event.CLASS_GROUP)
    except Event.DoesNotExist:
        raise Http404
    period = group.period
    return render(req, "applications/confirm_group.html", {
        "period": period,
        "group": group
    })


@login_required
@require_POST
def create_application(req):
    form = CreateApplication(req.POST)
    if form.is_valid():
        try:
            group = Event.objects.get(id=form.cleaned_data['group_id'], type=Event.CLASS_GROUP)
        except Event.DoesNotExist:
            raise HttpResponseNotAllowed
        try:
            ea = EventApplication.objects.get(user=req.user, event=group)
        except EventApplication.DoesNotExist:
            ea = EventApplication.objects.create(user=req.user, event=group)
            ea.save()
        if group.practiceexam:
            PracticeExamApplication.generate_for_user(req.user, group.practiceexam).save()
        return redirect(reverse('applications_group_application', args=[group.id]))
    raise HttpResponseNotAllowed


@login_required
def group_application(req, group_id):
    try:
        group = Event.objects.get(id=group_id, type=Event.CLASS_GROUP, eventapplication__user=req.user)
        application = group.eventapplication_set.get(user=req.user)
    except Event.DoesNotExist:
        raise Http404
    except EventApplication.DoesNotExist:
        raise Http404
    return render(req, "applications/group_application.html", {
        "group": group,
        "application": application
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
        form = EventApplicationGeneric(req.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect(reverse('applications_group_application', args=[group_id]))
    else:
        form = EventApplicationGeneric(instance=application)
    return render(req, "applications/group_application_edit_info.html", {
        "group": group,
        "application": application,
        "form": form
    })