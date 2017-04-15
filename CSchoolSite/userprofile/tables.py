from django.contrib.auth.models import Group
from django.db.models import Q
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.translation import ugettext_lazy as _

from userprofile.models import Relationship, User
from userprofile.utils import is_group_member

from main.enums import APPROVED


class PossibleRelativesTable(BaseDatatableView):
    max_display_length = 50

    # yep, we need to redefine existed column for custom data (even for buttons!)
    columns = ['username', 'first_name', 'birthday', 'created']
    order_columns = ['username', 'first_name', 'birthday', '']

    # get data
    def get_initial_queryset(self):
        user = self.request.user

        # # check is user parent or child
        # excluded_id_list = []
        # exclude_children = []
        # exclude_parents = []
        # exclude_families = []
        #
        # # parents_users = Group.objects.get(name=_('Parents')).user_set.values_list('id', flat=True)
        #
        # # try:
        # #   exclude_children = Relationship.objects.filter(relative=user.id).values_list('child', flat=True)
        # #    # exclude_child = [value for value in exclude_child if value not in parents_users]
        # # except Relationship.DoesNotExist:
        # #    pass
        #
        # try:
        #     exclude_parents = Relationship.objects.filter(child=user.id).values_list('relative', flat=True)
        #     # exclude_parent = [value for value in exclude_parent if value not in parents_users]
        # except Relationship.DoesNotExist:
        #     pass
        #
        # try:
        #     exclude_children = Relationship.objects.values_list('child', flat=True)
        # except Relationship.DoesNotExist:
        #     pass
        #
        # excluded_id_list.append(user.id)
        # excluded_id_list.extend(exclude_children)
        # excluded_id_list.extend(exclude_parents)

        excluded_id_list = []
        exclude_parents = []
        exclude_children = []

        if is_group_member(user, _('Parents')):
            # remove all user's children
            try:
                exclude_children = Relationship.objects.filter(relative=user.id).values_list('child', flat=True)
            except Relationship.DoesNotExist:
                pass

            exclude_parents = Relationship.objects.values_list('relative', flat=True)

        if is_group_member(user, _('Students')):
            # remove all user's parents
            try:
                exclude_parents = Relationship.objects.filter(child=user.id).values_list('relative', flat=True)
            except Relationship.DoesNotExist:
                pass

            # remove all children
            exclude_children = Relationship.objects.values_list('child', flat=True)

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
            return '<button type="button" class="btn btn-primary" data-relative="{}">{}</button>' \
                .format(row.id, _('Send relationship request'))
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
                # children doesn't know parents yet
                if row.request != APPROVED:
                    return _('Unknown')
                else:
                    return row.status
        elif column == 'modified':
            if row.request != APPROVED:
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
