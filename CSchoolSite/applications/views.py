from django.shortcuts import render
from applications.models import Period


def choose_period(req):
    periods = Period.objects.all().order_by("-begin")
    return render(req, "applications/choose_period.html", {
        "periods": periods
    })