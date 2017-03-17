from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.translation import ugettext_lazy as _

from userprofile.models import Relationship, User


class PossibleRelativesTable(BaseDatatableView):
    max_display_length = 50

    # yep, we need to redefine existed column for custom data (even for buttons!)
    columns = ['username', 'first_name', 'birthday', 'modified', 'created']
    order_columns = ['username', 'first_name', 'birthday', '', '']

    # get data
    def get_initial_queryset(self):
        user = self.request.user

        # check is user parent or child
        excluded_id_list = []
        exclude_child = []
        exclude_parent = []

        try:
            print(Relationship.objects.get(relative=user.id))
            exclude_child = Relationship.objects.filter(relative=user.id).values_list('child', flat=True)
        except Relationship.DoesNotExist:
            pass

        try:
            print(Relationship.objects.get(child=user.id))
            exclude_parent = Relationship.objects.filter(child=user.id).values_list('relative', flat=True)
        except Relationship.DoesNotExist:
            pass

        excluded_id_list.append(user.id)
        excluded_id_list.extend(exclude_child)
        excluded_id_list.extend(exclude_parent)

        # exclude id from users
        return User.objects.exclude(id__in=excluded_id_list)

    # redefine column data
    def render_column(self, row, column):
        if column == 'first_name':
            return '{}'.format(row.get_initials())
        elif column == 'modified':
            return '<select class="form-control"><option value="parent">{}</option>' \
                   '<option value="child">{}</option></select>'.format(_('Parent'), _('Child'))
        elif column == 'created':
            return '<button type="button" class="btn btn-primary" data-relative="{}">{}</button>' \
                .format(row.id, _('Send relationship request'))
        else:
            return super(PossibleRelativesTable, self).render_column(row, column)


#class RelationshipTable(BaseDatatableView):
