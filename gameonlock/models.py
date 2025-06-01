from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from localflavor.us.models import USStateField
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    state = USStateField(_("state"), blank=True, null=True)
    date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
    phone_number = PhoneNumberField(_("phone number"), blank=True, null=True)
    alternate_email_address = models.EmailField(
        _("alternate email address"), blank=True, null=True
    )
