from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


def create_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission

    permissions_list = ['add', 'change', 'delete', 'view']
    model_name = 'campvoucher'
    group, created = Group.objects.get_or_create(name=_('Комитет образования'))

    for permission_name in permissions_list:
        try:
            permission = Permission.objects.get(codename="{}_{}".format(permission_name, model_name))
            if permission not in group.permissions.all():
                group.permissions.add(permission)
        except Exception:
            pass


class ApplicationsConfig(AppConfig):
    name = 'applications'
    verbose_name = 'Заявки'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(create_groups, sender=self)
