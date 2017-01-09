from django.apps import AppConfig

from django.utils.translation import ugettext_lazy as _


def create_permissions(permissions_list, model_name):
    from django.contrib.auth.models import Permission
    return [Permission.objects.get(codename="{}_{}".format(permission, model_name)) for permission in permissions_list]


def create_groups(sender, **kwargs):
    import logging
    from django.contrib.auth.models import Group, Permission

    group, created = Group.objects.get_or_create(name=_('Комитет образования'))

    if created:
        permissions = create_permissions(['add', 'change', 'delete', 'view'], 'campvoucher')
        for permission in permissions:
            if permission not in group.permissions:
                group.permissions.add(permission)
    else:
        logging.error('Cannot create group for committee!')


class ApplicationsConfig(AppConfig):
    name = 'applications'
    verbose_name = 'Заявки'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(create_groups, sender=self)
