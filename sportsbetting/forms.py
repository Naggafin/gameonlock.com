from django import forms
from django.conf import settings
from django.forms import modelformset_factory
from django.utils.translation import get_language, gettext_lazy as _, to_locale
from moneyed.l10n import format_money

from .models import Play, PlayPick


class PlayForm(forms.ModelForm):
	def clean_amount(self):
		amount = self.cleaned_data.get("amount")
		if not amount or amount < settings.SPORTS["MIN_BET"]:
			locale = to_locale(get_language())
			raise forms.ValidationError(
				_("Bet amount must be at least %(min_amount)s.")
				% {"min_amount": format_money(settings.SPORTS["MIN_BET"], locale)}
			)
		return amount

	class Meta:
		model = Play
		fields = ["amount"]


PlayPickFormSet = modelformset_factory(
	PlayPick,
	fields=["betting_line", "type", "team", "is_over"],
	extra=0,
	absolute_max=1500,
)
