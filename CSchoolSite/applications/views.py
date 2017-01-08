from django.http import Http404
from django.shortcuts import render
from applications.models import Period, Event


def choose_period(req):
    periods = Period.objects.all().order_by("-begin")
    return render(req, "applications/choose_period.html", {
        "periods": periods
    })


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