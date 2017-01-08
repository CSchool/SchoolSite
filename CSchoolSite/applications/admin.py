from django.contrib import admin
from django.db import models
from tinymce.widgets import AdminTinyMCE

from applications.models import Period, CampVoucher, Event


class PeriodAdmin(admin.ModelAdmin):
    pass
admin.site.register(Period, PeriodAdmin)


class CampVoucherAdmin(admin.ModelAdmin):
    pass
admin.site.register(CampVoucher, CampVoucherAdmin)


class EventAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()},
    }

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
admin.site.register(Event, EventAdmin)