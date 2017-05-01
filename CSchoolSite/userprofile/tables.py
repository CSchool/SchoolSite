from django.contrib.auth.models import Group
from django.db.models import Q
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.translation import ugettext_lazy as _
from django.middleware.csrf import get_token

from userprofile.models import Relationship, User
from userprofile.utils import is_group_member


class RelationshipTable(BaseDatatableView):
    columns = ['relative', 'reltype', 'modified']
    order_columns = ['relative', '', '']

    def get_initial_queryset(self):
        user = self.request.user
        return Relationship.objects.filter(Q(relative=user) | Q(child=user)).filter(relative__isnull=False, child__isnull=False)

    def render_column(self, row, column):
        user = self.request.user
        if column == 'relative':
            relative = row.relative if user == row.child else row.child

            if relative.get_initials():
                return "{} ({})".format(relative.username, relative.get_initials())
            else:
                return relative.username
        elif column == 'reltype':
            if row.relative == user:
                return _('Child')
            else:
                return _('Parent')
        elif column == 'modified':
            # if row.request != Relationship.APPROVED:
            #     # acceptation link or nothing
            #     if row.invited_user == user:
            #         relative = row.relative if row.invited_user == row.child else row.child
            #         return '<a href="{}" class="btn btn-primary btn-xs" role="button">{}</a>'.format(
            #             reverse('relationship_acceptance', args=[relative]), _('Accept'))
            #     else:
            #         return ''
            # else:
            #     # view profile or nothing
            #     # if row.relative == user and is_group_member(row.relative, _('Parents')):
            #     #     return 'View profile'
            #     # else:
            #     #     return ''
            return '''
<form method="POST">
<input type="hidden" name="csrfmiddlewaretoken" value="{csrf}" />
<input type="hidden" name="delete_relation" value="{id}" />
<button type="submit" class="btn btn-danger btn-xs">
<span class="glyphicon glyphicon-remove"></span>
{delete}
</button>
</form>
'''.format(delete=_('Delete'), csrf=get_token(self.request), id=row.id)
        else:
            return super(RelationshipTable, self).render_column(row, column)
