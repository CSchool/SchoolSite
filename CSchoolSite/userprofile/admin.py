import logging

from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from userprofile.forms import AdminUserChangeForm, AdminUserAddForm
from .models import User, Relationship


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    form = AdminUserChangeForm
    add_form = AdminUserAddForm
    readonly_fields = ('telegram_username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name',
            'last_name',
            'patronymic',
            'birthday',
            'email',
            'phone',
            'alias',
            'telegram_username'
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'personal',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
         ),
    )


admin.site.register(User, UserAdmin)


class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_relative_link', 'get_child_link', 'invited_user', 'request', 'confirmation_code', 'valid_until')
    search_fields = ('id', 'relative', 'child', 'invited_user', 'status', 'request')

    def get_relative_link(self, object):
        if object.relative:
            link = urlresolvers.reverse('admin:userprofile_user_change', args=[object.relative.id])
            return '<a href={}>{}</a>'.format(link, object.relative.username)
        else:
            return '&mdash;'

    get_relative_link.allow_tags = True
    get_relative_link.admin_order_field = 'relative'
    get_relative_link.short_description = _('Relative')

    def get_child_link(self, object):
        if object.child:
            link = urlresolvers.reverse('admin:userprofile_user_change', args=[object.child.id])
            return '<a href={}>{}</a>'.format(link, object.child.username)
        else:
            return '&mdash;'

    get_child_link.allow_tags = True
    get_child_link.admin_order_field = 'child'
    get_child_link.short_description = _('Child')

admin.site.register(Relationship, RelationshipAdmin)
