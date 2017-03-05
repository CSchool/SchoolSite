from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.translation import ugettext_lazy as _

from userprofile.models import Relationship, User


class PossibleRelativesTable(BaseDatatableView):
    max_display_length = 50

    # yep, we need to redefine existed column for custom data (even for buttons!)
    columns = ['username', 'first_name', 'birthday', 'created']
    order_columns = ['username', 'first_name', 'birthday', '']

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

    # redefine column data
    def render_column(self, row, column):
        if column == 'first_name':
            return '{}'.format(row.get_initials())
        elif column == 'created':
            return '<button type="button" class="btn btn-primary" data-relative="{}">{}</button>'\
                    .format(row.id, _('Send relationship request'))
        else:
            return super(PossibleRelativesTable, self).render_column(row, column)
