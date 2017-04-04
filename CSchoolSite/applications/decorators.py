from functools import wraps

from django.shortcuts import redirect, reverse

from applications.models import Event, Period, EventApplication


def study_group_application(func):
    @wraps(func)
    def decorated(req, **kwargs):
        try:
            group_id = kwargs.get('group_id')
            if group_id is None:
                period_id = kwargs.get('period_id')
                period = Period.objects.get(id=period_id)
            else:
                group = Event.objects.get(id=group_id)
                period = group.period
            f = EventApplication.objects.filter(user=req.user, event__type=Event.CLASS_GROUP, event__period=period)
            if f:
                return redirect('applications_group_application', group_id=f.get().event_id)
        except:
            pass
        return func(req, **kwargs)
    return decorated