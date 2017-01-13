from django.contrib import admin
from django.db import models
from tinymce.widgets import AdminTinyMCE

from applications.models import Period, CampVoucher, Event, EventApplication, PracticeExam, PracticeExamRun
from applications.models import PracticeExamProblem
from applications.models import TheoryExam, TheoryExamQuestion, TheoryExamQuestionOption


admin.site.register(Period)
admin.site.register(CampVoucher)


class EventAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()},
    }

admin.site.register(Event, EventAdmin)


class EventApplicationAdmin(admin.ModelAdmin):
    exclude = ('practice_exam',)

admin.site.register(EventApplication, EventApplicationAdmin)
admin.site.register(PracticeExam)
admin.site.register(PracticeExamProblem)
admin.site.register(PracticeExamRun)


class TheoryExamQuestionOptionInline(admin.TabularInline):
    model = TheoryExamQuestionOption


class TheoryExamQuestionAdmin(admin.ModelAdmin):
    inlines = [
        TheoryExamQuestionOptionInline
    ]

admin.site.register(TheoryExamQuestion, TheoryExamQuestionAdmin)
admin.site.register(TheoryExam)