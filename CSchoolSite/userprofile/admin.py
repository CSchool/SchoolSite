import logging

from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

from userprofile.forms import AdminUserChangeForm, AdminUserAddForm
from .models import User, Relationship


class UserAdmin(BaseUserAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserAddForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name',
            'last_name',
            'patronymic',
            'birthday',
            'email',
            'phone'
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
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
    list_display = ('id', 'relative', 'child', 'invited_user', 'status', 'request')
    search_fields = ('id', 'relative', 'child', 'invited_user', 'status', 'request')
    #list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')


admin.site.register(Relationship, RelationshipAdmin)
