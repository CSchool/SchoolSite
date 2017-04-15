from django.utils.translation import ugettext_lazy as _

WAITING = 'WT'
APPROVED = 'AP'
DECLINED = 'DC'

REQUEST_STATUS = (
    (WAITING, _('Waiting')),
    (APPROVED, _('Approved')),
    (DECLINED, _('Declined'))
)