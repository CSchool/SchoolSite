from django.contrib import admin
from django.db import models

from news.models import NewsPost
from tinymce.widgets import AdminTinyMCE


class NewsPostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE()},
    }
    list_display = ('title', 'body', 'user')
    readonly_fields = ('user', 'modified')

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
admin.site.register(NewsPost, NewsPostAdmin)