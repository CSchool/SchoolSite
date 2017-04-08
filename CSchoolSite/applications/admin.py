from django.contrib import admin
from django.db import models
from tinymce.widgets import AdminTinyMCE

from applications.models import Period, CampVoucher, Event, EventApplication, PracticeExam, PracticeExamApplication
from applications.models import PracticeExamProblem
from applications.models import TheoryExam, TheoryExamQuestion, TheoryExamQuestionOption
from applications.forms import EventApplicationAdminForm


admin.site.register(Period)
admin.site.register(CampVoucher)


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

admin.site.register(TheoryExamQuestion, TheoryExamQuestionAdmin)
admin.site.register(TheoryExam)