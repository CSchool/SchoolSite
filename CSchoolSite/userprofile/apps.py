from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from CSchoolSite import settings


def create_permissions_list(permissions_list, model_name=None):
    from django.contrib.auth.models import Permission

    permissions = []

    for permission_name in permissions_list:
        try:
            permission = Permission.objects.get(
                codename="{}_{}".format(permission_name, model_name)) if model_name else \
                Permission.objects.get(codename=permission_name)
            permissions.append(permission)
        except Exception:
            pass

    return permissions


def create_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    from django.conf import settings
    from django.utils import translation

    translation.activate(settings.LANGUAGE_CODE)

    groups = [
        {'name': _('Education committee'),
         'permissions': create_permissions_list(['add', 'change', 'delete', 'view'], 'campvoucher')},
        {'name': _('Students'), 'permissions': create_permissions_list(['can_submit_application'])},
        {'name': _('Parents'), 'permissions': []}
    ]

    for group_element in groups:
        group, created = Group.objects.get_or_create(name=group_element['name'])
        for permission in group_element['permissions']:
            if permission not in group.permissions.all():
                group.permissions.add(permission)

    translation.deactivate()


def set_default_group(sender, **kwargs):
    from django.contrib.auth.models import Group

    user = kwargs["instance"]
    if kwargs["created"] and not user.is_staff:
        group = Group.objects.get(name=_('Students'))
        user.groups.add(group)


class UserProfileConfig(AppConfig):
    name = 'userprofile'
    verbose_name = _('Profiles_and_groups')

    def ready(self):
        from django.db.models.signals import post_migrate
        from userprofile.models import User
        from django.apps import apps

        post_migrate.connect(create_groups, sender=self)
        post_save.connect(set_default_group, sender=User)

        apps.get_app_config('registration').verbose_name = _("Registration")
