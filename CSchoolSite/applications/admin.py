from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import AdminTinyMCE

from applications.models import Period, Event, EventApplication, PracticeExam, PracticeExamApplication, \
    PracticeExamRun, PeriodAttachment
from applications.models import PracticeExamProblem
from applications.models import TheoryExam, TheoryExamQuestion, TheoryExamQuestionOption
from applications.forms import EventApplicationAdminForm, PracticeExamRunAdminForm


class EventAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()},
    }

admin.site.register(Event, EventAdmin)


class EventApplicationAdmin(admin.ModelAdmin):
    form = EventApplicationAdminForm
    list_display = ('__str__', 'get_period_name', 'status')
    list_filter = ('event__period__name', 'status')
    actions = ('make_accepted', 'make_enrolled', 'make_issued', 'make_studying')

    def has_add_permission(self, request):
        return False

    def get_period_name(self, instance):
        return instance.event.period.name
    get_period_name.short_description = _('Period')
    get_period_name.admin_order_field = 'event__period__name'

    def make_accepted(self, request, queryset):
        queryset.update(status=EventApplication.ACCEPTED)
    make_accepted.short_description = _('Mark selected applications as Accepted')

    def make_enrolled(self, request, queryset):
        queryset.update(status=EventApplication.ENROLLED)
    make_enrolled.short_description = _('Mark selected applications as Enrolled')

    def make_issued(self, request, queryset):
        queryset.update(status=EventApplication.ISSUED)
    make_issued.short_description = _('Mark selected applications as Issued')

    def make_studying(self, request, queryset):
        queryset.update(status=EventApplication.STUDYING)
    make_studying.short_description = _('Mark selected applications as Studying')

admin.site.register(EventApplication, EventApplicationAdmin)
admin.site.register(PracticeExam)
admin.site.register(PracticeExamProblem)


class PeriodAttachmentInline(admin.TabularInline):
    model = PeriodAttachment
    fields = ('name', 'file', 'type')


class PeriodAdmin(admin.ModelAdmin):
    inlines = [
        PeriodAttachmentInline
    ]


admin.site.register(Period, PeriodAdmin)


class TheoryExamQuestionOptionInline(admin.TabularInline):
    model = TheoryExamQuestionOption


class TheoryExamQuestionAdmin(admin.ModelAdmin):
    inlines = [
        TheoryExamQuestionOptionInline
    ]
    formfield_overrides =  {
        models.TextField: {'widget': AdminTinyMCE()},
    }


class PracticeExamRunAdmin(admin.ModelAdmin):
    form = PracticeExamRunAdminForm
    readonly_fields = ('user', 'ejudge_run_id', 'problem')
    list_display = ('__str__', 'ejudge_run_id',)

    def has_add_permission(self, request):
        return False

admin.site.register(TheoryExamQuestion, TheoryExamQuestionAdmin)
admin.site.register(TheoryExam)
admin.site.register(PracticeExamRun, PracticeExamRunAdmin)