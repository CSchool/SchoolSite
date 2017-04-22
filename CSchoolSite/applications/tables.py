from django.http import Http404
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView

from applications.models import EventApplication, Period, Event


class EnrolledTable(BaseDatatableView):
    max_display_length = 200

    columns = ('user', 'event', 'status', 'color', 'group_id', 'status_id')
    order_columns = ('user', 'event__difficulty', 'status', '', '', '')

    def get_initial_queryset(self):
        user = self.request.user
        try:
            period = Period.objects.get(id=self.request.resolver_match.kwargs.get('period_id'))
        except Period.DoesNotExist:
            raise Http404
        applications = EventApplication.objects \
            .filter(event__period=period) \
            .filter(event__type=Event.CLASS_GROUP) \
            .filter(status__in=EventApplication.ENROLLED_STATUSES)
        if user.is_authenticated and user.is_education_committee:
            applications = applications.order_by('user__last_name', 'user__first_name')
        else:
            applications = applications.order_by('event__difficulty', 'user__last_name', 'user__first_name')
        return applications

    def filter_queryset(self, qs):
        for k in range(len(self.columns)):
            column = self.columns[k]
            search_val = self.request.GET.get('columns[%d][search][value]' % k)
            if search_val:
                if column == 'group_id':
                    qs = qs.filter(event_id=search_val)
                if column == 'status_id':
                    qs = qs.filter(status=search_val)
        return qs

    def render_column(self, row, column):
        if column == 'user':
            return row.user.get_initials()
        if column == 'event':
            return row.event.name
        if column == 'status':
            if self.request.user.is_authenticated and (self.request.user.is_education_committee or self.request.user.is_superuser):
                return '''
                    <a href="{}">{}</a>
                '''.format(reverse('applications_group_application_edu', args=[row.id]), row.get_status_display())
            else:
                return row.get_status_display()
        if column == 'color':
            return row.enrolled_color
        if column == 'group_id':
            return row.event.id
        if column == 'status_id':
            return row.status
        return super(EnrolledTable, self).render_column(row, column)