from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
	country = CountryField(_("country"))
	region = models.CharField(_("region"), max_length=50)
	date_of_birth = models.DateField(_("date of birth"))
	phone_number = PhoneNumberField(_("phone number"), blank=True, null=True)
	alternate_email_address = models.EmailField(
		_("alternate email address"), blank=True, null=True
	)

	def get_region_display(self):
		from gameonlock.forms import REGION_CHOICES

		country_code = (
			self.country.code if hasattr(self.country, "code") else str(self.country)
		)
		regions = dict(REGION_CHOICES.get(country_code, []))
		return regions.get(self.region, self.region or _("(Unknown Region)"))
