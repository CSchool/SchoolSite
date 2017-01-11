# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from main.models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_patronymic', 'get_birthday', 'is_staff',)
    list_select_related = ('userprofile',)  # important!

    def get_birthday(self, instance):
        return instance.userprofile.birthday

    get_birthday.short_description = _('birthday')

    def get_patronymic(self, instance):
        return instance.userprofile.patronymic

    get_patronymic.short_description = _('patronymic')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
