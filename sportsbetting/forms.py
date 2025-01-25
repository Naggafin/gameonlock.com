from django import forms
from django.forms import modelformset_factory

from .models import SpreadPick, TicketPlay, UnderOverPick


class TicketPlayForm(forms.ModelForm):
	class Meta:
		model = TicketPlay
		fields = ["purchaser_name", "email", "phone", "bet_amount"]

	def clean_bet_amount(self):
		amount = self.cleaned_data.get("bet_amount")
		if amount is None or amount < 5.0:
			raise forms.ValidationError("Bet amount must be at least $5.00.")
		return amount


SpreadPickFormSet = modelformset_factory(
	SpreadPick, fields=["picked", "spread_entry"], extra=0, can_delete=False
)

UnderOverPickFormSet = modelformset_factory(
	UnderOverPick,
	fields=["under_or_over", "under_over_entry"],
	extra=0,
	can_delete=False,
)
