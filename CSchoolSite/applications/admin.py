from django.contrib import admin

from applications.models import Period, CampVoucher


class PeriodAdmin(admin.ModelAdmin):
    pass
admin.site.register(Period, PeriodAdmin)


class CampVoucherAdmin(admin.ModelAdmin):
    pass
admin.site.register(CampVoucher, CampVoucherAdmin)