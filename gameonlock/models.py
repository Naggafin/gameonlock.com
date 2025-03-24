from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from localflavor.us.models import USStateField
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
	state = USStateField(_("state"))
	date_of_birth = models.DateField(_("date of birth"))
	phone_number = PhoneNumberField(_("phone number"), blank=True)
	alternate_email_address = models.EmailField(
		_("alternate email address"), blank=True
	)
