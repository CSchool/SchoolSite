from django.contrib.auth.models import Group
from django.db.models import Q
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.translation import ugettext_lazy as _

from userprofile.models import Relationship, User
from userprofile.utils import is_group_member


class PossibleRelativesTable(BaseDatatableView):
    max_display_length = 50

    # yep, we need to redefine existed column for custom data (even for buttons!)
    columns = ['username', 'first_name', 'birthday', 'created']
    order_columns = ['username', 'first_name', 'birthday', '']

    # get data
    def get_initial_queryset(self):
        user = self.request.user

        excluded_id_list = []
        exclude_parents = []
        exclude_children = []

        if is_group_member(user, _('Parents')):
            # remove all user's children
            try:
                exclude_children = Relationship.objects.filter(relative=user.id).values_list('child', flat=True)
            except Relationship.DoesNotExist:
                pass

        if is_group_member(user, _('Students')):
            # remove all user's parents
            try:
                exclude_parents = Relationship.objects.filter(child=user.id).values_list('relative', flat=True)
            except Relationship.DoesNotExist:
                pass

        excluded_id_list.extend(exclude_parents)
        excluded_id_list.extend(exclude_children)
        excluded_id_list.append(user.id)

        # exclude id from users
        return User.objects.exclude(id__in=excluded_id_list)

    # redefine column data
    def render_column(self, row, column):
        if column == 'first_name':
            return '{}'.format(row.get_initials())
        elif column == 'created':
            return '''
            <div class="dropdown">
            <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                {req_text}
                <span class="caret"></span>
            </button>
            <ul class="dropdown-menu">
                <li><a class="datatables_send_parent" href="#"  data-relative="{row_id}">{parent_text}</a></li>
                <li><a class="datatables_send_child" href="#"  data-child="{row_id}">{child_text}</a></li>
            </ul>
            </div>
            ''' \
                .format(
                    row_id=row.id,
                    req_text=_('Send relationship request'),
                    parent_text=_('This is my parent'),
                    child_text=_('This is my child')
            )
        else:
            return super(PossibleRelativesTable, self).render_column(row, column)


class RelationshipTable(BaseDatatableView):
    columns = ['relative', 'status', 'request', 'modified']
    order_columns = ['relative', 'status', 'request', '']

    def get_initial_queryset(self):
        user = self.request.user
        return Relationship.objects.filter(Q(relative=user) | Q(child=user))

    def render_column(self, row, column):
        user = self.request.user
        if column == 'relative':
            relative = row.relative if user == row.child else row.child

            if relative.get_initials():
                return "{} ({})".format(relative.username, relative.get_initials())
            else:
                return relative.username
        elif column == 'status':
            if row.relative == user:
                # parents know their children
                return _('Child')
            else:
                return _('Parent')
        elif column == 'modified':
            if row.request != Relationship.APPROVED:
                # acceptation link or nothing
                if row.invited_user == user:
                    relative = row.relative if row.invited_user == row.child else row.child
                    return '<a href="{}" class="btn btn-primary btn-xs" role="button">{}</a>'.format(
                        reverse('relationship_acceptance', args=[relative]), _('Accept'))
                else:
                    return ''
            else:
                # view profile or nothing
                if row.relative == user and is_group_member(row.relative, _('Parents')):
                    return 'View profile'
                else:
                    return ''
        else:
            return super(RelationshipTable, self).render_column(row, column)
