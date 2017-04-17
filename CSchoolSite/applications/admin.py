from django.contrib import admin
from django.db import models
from tinymce.widgets import AdminTinyMCE

from applications.models import Period, Event, EventApplication, PracticeExam, PracticeExamApplication, \
    PracticeExamRun
from applications.models import PracticeExamProblem
from applications.models import TheoryExam, TheoryExamQuestion, TheoryExamQuestionOption
from applications.forms import EventApplicationAdminForm, PracticeExamRunAdminForm


admin.site.register(Period)


class EventAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()},
    }

admin.site.register(Event, EventAdmin)


class EventApplicationAdmin(admin.ModelAdmin):
    form = EventApplicationAdminForm
    readonly_fields = ('user', 'event')

    def has_add_permission(self, request):
        return False

admin.site.register(EventApplication, EventApplicationAdmin)
admin.site.register(PracticeExam)
admin.site.register(PracticeExamProblem)


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