from functools import wraps

from django.http import Http404
from django.shortcuts import redirect, reverse

from applications.models import Event, Period, EventApplication
from userprofile.models import User


def study_group_application(func):
    @wraps(func)
    def decorated(req, **kwargs):
        try:
            group_id = kwargs.get('group_id')
            username = kwargs.get('username')
            if username is None:
                user = req.user
            else:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    raise Http404
            if group_id is None:
                period_id = kwargs.get('period_id')
                period = Period.objects.get(id=period_id)
            else:
                group = Event.objects.get(id=group_id)
                period = group.period
            f = EventApplication.objects.filter(user=user, event__type=Event.CLASS_GROUP, event__period=period)
            if f.exists():
                return redirect(reverse('applications_group_application', args=[f.get().id]))
        except:
            pass
        return func(req, **kwargs)
    return decorated