from django import forms
from django.conf import settings
from django.forms import inlineformset_factory
from django.utils.translation import get_language, gettext_lazy as _, to_locale
from moneyed.l10n import format_money

from .models import Pick, Play


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


class PickForm(forms.ModelForm):
	class Meta:
		model = Pick
		fields = ["betting_line", "type", "team", "is_over"]


# Inline formset (Play is the parent, Pick is the child)
PickFormSet = inlineformset_factory(
	Play,
	Pick,
	form=PickForm,
	extra=0,
)
