from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.translation import ugettext_lazy as _

from userprofile.models import Relationship, User


class PossibleRelativesTable(BaseDatatableView):
    max_display_length = 50

    # yep, we need to redefine existed column for custom data (even for buttons!)
    columns = ['username', 'first_name', 'birthday']
    order_columns = ['username', 'first_name', 'birthday']

    # get data
    def get_initial_queryset(self):
        user = self.request.user

        # check is user parent or child
        excluded_id_list = []
        if user.groups.filter(name=_('Parents')).exists():
            excluded_id_list = Relationship.objects.filter(relative=user.id).values('child')
        elif user.groups.filter(name=_('Students')).exists():
            excluded_id_list = Relationship.objects.filter(child=user.id).values('relative')

        excluded_id_list.append(user.id)

        # exclude id from users
        return User.objects.exclude(id__in=excluded_id_list)

    # change some columns (here redefinition comes to play)
    def prepare_results(self, qs):
        json_data = []

        for item in qs:
            full_name = '{} {} {}'.format(item.last_name, item.first_name, item.patronymic).strip()
            json_data.append([item.username, full_name, item.birthday])

        return json_data
