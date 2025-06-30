import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from gameonlock.forms import get_all_region_choices


def generate_referral_id(length=8):
	chars = string.ascii_uppercase + string.digits
	return "".join(random.choices(chars, k=length))


class User(AbstractUser):
	country = CountryField(_("country"), blank=True, null=True)
	region = models.CharField(_("region"), max_length=50, blank=True, null=True)
	date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
	phone_number = PhoneNumberField(_("phone number"), blank=True, null=True)
	alternate_email_address = models.EmailField(
		_("alternate email address"), blank=True, null=True
	)
	referral_id = models.CharField(max_length=12, unique=True, blank=True, null=True)
	referred_by = models.CharField(max_length=12, blank=True, null=True)

	def get_region_display(self):
		regions = get_all_region_choices()
		country_code = (
			self.country.code if hasattr(self.country, "code") else str(self.country)
		)
		regions = dict(regions.get(country_code, []))
		return regions.get(self.region, self.region or _("(Unknown Region)"))

	def save(self, *args, **kwargs):
		if not self.referral_id:
			self.referral_id = self._generate_unique_referral_id()
		super().save(*args, **kwargs)

	def _generate_unique_referral_id(self):
		while True:
			referral_id = generate_referral_id()
			if not User.objects.filter(referral_id=referral_id).exists():
				return referral_id
