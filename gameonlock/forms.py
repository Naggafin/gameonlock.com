from datetime import date

from allauth.account.forms import SignupForm as AllauthSignupForm
from cache_memoize import cache_memoize
from django import forms
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_fastdev import fastdev_ignore
from localflavor.ar.forms import ARProvinceSelect
from localflavor.at.forms import ATStateSelect
from localflavor.au.forms import AUStateSelect
from localflavor.be.forms import BEProvinceSelect
from localflavor.br.forms import BRStateField
from localflavor.ca.forms import CAProvinceField
from localflavor.ch.forms import CHStateSelect
from localflavor.cl.forms import CLRegionSelect
from localflavor.cn.forms import CNProvinceSelect
from localflavor.co.forms import CODepartmentSelect
from localflavor.cz.forms import CZRegionSelect
from localflavor.de.forms import DEStateField
from localflavor.dk.forms import DKRegionSelect
from localflavor.ec.forms import ECProvinceSelect
from localflavor.ee.forms import EECountySelect
from localflavor.es.forms import ESProvinceSelect
from localflavor.fi.forms import FIRegionSelect
from localflavor.fr.forms import FRDepartmentSelect
from localflavor.gb.forms import GBCountySelect
from localflavor.gr.forms import GRRegionSelect
from localflavor.hr.forms import HRCountySelect
from localflavor.hu.forms import HURegionSelect
from localflavor.id.forms import IDProvinceSelect
from localflavor.ie.forms import IECountySelect
from localflavor.il.forms import ILAreaSelect
from localflavor.in_.forms import INStateField
from localflavor.is_.forms import ISRegionSelect
from localflavor.it.forms import ITRegionSelect
from localflavor.jp.forms import JPPrefectureField
from localflavor.kw.forms import KWSubdivisionSelect
from localflavor.lt.forms import LTCountySelect
from localflavor.lv.forms import LVRegionSelect
from localflavor.mk.forms import MKMunicipalitySelect
from localflavor.mt.forms import MTRegionSelect
from localflavor.mx.forms import MXStateField
from localflavor.nl.forms import NLProvinceField
from localflavor.no.forms import NOCountySelect
from localflavor.nz.forms import NZRegionSelect
from localflavor.pe.forms import PERegionSelect
from localflavor.pk.forms import PKProvinceSelect
from localflavor.pl.forms import PLVoivodeshipSelect
from localflavor.pt.forms import PTRegionSelect
from localflavor.py.forms import PYDepartmentSelect
from localflavor.ro.forms import ROCountySelect
from localflavor.ru.forms import RURegionSelect
from localflavor.se.forms import SECountySelect
from localflavor.si.forms import SICountySelect
from localflavor.sk.forms import SKRegionSelect
from localflavor.tn.forms import TNGovernorateSelect
from localflavor.tr.forms import TRProvinceSelect
from localflavor.us.forms import USStateField
from localflavor.uy.forms import UYDepartmentSelect
from localflavor.za.forms import ZAProvinceSelect
from phonenumber_field.formfields import PhoneNumberField

# Map country codes to their respective django-localflavor field classes
COUNTRY_REGION_FIELDS = {
	"AR": ARProvinceSelect,
	"AT": ATStateSelect,
	"AU": AUStateSelect,
	"BE": BEProvinceSelect,
	"BR": BRStateField,
	"CA": CAProvinceField,
	"CH": CHStateSelect,
	"CL": CLRegionSelect,
	"CN": CNProvinceSelect,
	"CO": CODepartmentSelect,
	"CZ": CZRegionSelect,
	"DE": DEStateField,
	"DK": DKRegionSelect,
	"EC": ECProvinceSelect,
	"EE": EECountySelect,
	"ES": ESProvinceSelect,
	"FI": FIRegionSelect,
	"FR": FRDepartmentSelect,
	"GB": GBCountySelect,
	"GR": GRRegionSelect,
	"HR": HRCountySelect,
	"HU": HURegionSelect,
	"ID": IDProvinceSelect,
	"IE": IECountySelect,
	"IL": ILAreaSelect,
	"IN": INStateField,
	"IS": ISRegionSelect,
	"IT": ITRegionSelect,
	"JP": JPPrefectureField,
	"KW": KWSubdivisionSelect,
	"LT": LTCountySelect,
	"LV": LVRegionSelect,
	"MK": MKMunicipalitySelect,
	"MT": MTRegionSelect,
	"MX": MXStateField,
	"NL": NLProvinceField,
	"NO": NOCountySelect,
	"NZ": NZRegionSelect,
	"PE": PERegionSelect,
	"PK": PKProvinceSelect,
	"PL": PLVoivodeshipSelect,
	"PT": PTRegionSelect,
	"PY": PYDepartmentSelect,
	"RO": ROCountySelect,
	"RU": RURegionSelect,
	"SE": SECountySelect,
	"SI": SICountySelect,
	"SK": SKRegionSelect,
	"TN": TNGovernorateSelect,
	"TR": TRProvinceSelect,
	"US": USStateField,
	"UY": UYDepartmentSelect,
	"ZA": ZAProvinceSelect,
}


@cache_memoize(None)
def get_all_region_choices():
	"""
	Returns a dictionary mapping each country code to a list of region choices,
	excluding any default empty choice like ('', 'Select...').
	"""
	region_choices = {}

	for country_code, region_field_class in COUNTRY_REGION_FIELDS.items():
		try:
			field_instance = region_field_class()
			choices = list(field_instance.choices)

			# Filter out any empty default option (typically first)
			cleaned_choices = [
				(value, label) for value, label in choices if value != ""
			]

			region_choices[country_code] = cleaned_choices
		except Exception as e:
			region_choices[country_code] = []
			print(f"Failed to get choices for {country_code}: {e}")

	return region_choices


@fastdev_ignore
class SignupForm(AllauthSignupForm):
	first_name = forms.CharField(max_length=100, label=_("First Name"))
	last_name = forms.CharField(max_length=100, label=_("Last Name"))
	country = CountryField(label=_("Country"), initial="US").formfield()
	region = forms.ChoiceField(
		label=_("State/Province"), choices=[("", "Select Region")]
	)
	date_of_birth = forms.DateField(
		label=_("Date of Birth"), widget=forms.DateInput(attrs={"type": "date"})
	)
	phone_number = PhoneNumberField(required=False, label=_("Phone Number"))
	alternate_email_address = forms.EmailField(
		required=False, label=_("Alternate Email Address")
	)
	terms = forms.BooleanField(label=_("I agree to the terms and conditions"))
	age = forms.BooleanField(label=_("I confirm I am at least 18 years old"))

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Determine country code from submitted data or initial value
		country_code = self.data.get(
			"country", self.initial.get("country", "US") or "US"
		)

		# Hot swap the region field based on country
		region_field_class = COUNTRY_REGION_FIELDS.get(country_code)
		if region_field_class:
			# Replace region field with country-specific field
			self.fields["region"] = region_field_class(
				label=_("State/Province"),
				required=True,
				# Ensure choices exclude empty option if present, as template handles 'Select Region'
				choices=region_field_class().choices[1:]
				if region_field_class().choices[0][0] == ""
				else region_field_class().choices,
			)
		else:
			# Fallback to generic ChoiceField for unsupported countries
			self.fields["region"] = forms.ChoiceField(
				label=_("State/Province"),
				choices=[("", "Select Region")],
				required=False,
			)

	def clean(self):
		cleaned_data = super().clean()
		country = cleaned_data.get("country")
		region = cleaned_data.get("region")
		date_of_birth = cleaned_data.get("date_of_birth")

		# Validate region using the region field's clean method
		if country and region:
			try:
				# Use the existing region field's clean method
				cleaned_data["region"] = self.fields["region"].clean(region)
			except forms.ValidationError as e:
				self.add_error("region", e)
		elif country and not region and COUNTRY_REGION_FIELDS.get(country):
			self.add_error("region", _("Region is required for the selected country."))
		elif region and not COUNTRY_REGION_FIELDS.get(country):
			self.add_error(
				"region", _("Region is not applicable for the selected country.")
			)

		# Validate user is at least 18 years old
		if date_of_birth:
			today = date.today()
			age = (
				today.year
				- date_of_birth.year
				- ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
			)
			if age < 18:
				self.add_error(
					"date_of_birth", _("You must be at least 18 years old to register.")
				)

		return cleaned_data

	def save(self, request):
		user = super().save(request)
		user.first_name = self.cleaned_data["first_name"]
		user.last_name = self.cleaned_data["last_name"]
		user.country = self.cleaned_data["country"]
		user.region = self.cleaned_data["region"]
		user.date_of_birth = self.cleaned_data["date_of_birth"]
		user.phone_number = self.cleaned_data["phone_number"]
		user.alternate_email_address = self.cleaned_data["alternate_email_address"]
		user.save()
		return user
