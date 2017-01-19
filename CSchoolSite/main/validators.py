from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


class PhoneValidator(RegexValidator):
    regex = r'^\+7 \([0-9]{3}\) [0-9]{3}\-[0-9]{2}\-[0-9]{2}$'
    message = _("The format of phone numbers is +7 (123) 456-78-90")
    code = 'invalid_phone_number'
