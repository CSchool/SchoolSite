from django.contrib import admin
from django.db import models
from tinymce.widgets import AdminTinyMCE

from applications.models import Period, CampVoucher, Event, EventApplication, PracticeExam
from applications.models import PracticeExamProblem


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

admin.site.register(Event, EventAdmin)

admin.site.register(EventApplication)
admin.site.register(PracticeExam)
admin.site.register(PracticeExamProblem)