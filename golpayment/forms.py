from django import forms
from django.utils.translation import gettext_lazy as _


class PayPalPaymentForm(forms.Form):
	amount = forms.DecimalField(
		max_digits=10,
		decimal_places=2,
		min_value=0.01,
		label=_("Amount"),
		help_text=_("Enter the amount you wish to pay."),
	)
	item_name = forms.CharField(
		max_length=127,
		label=_("Item Name"),
		help_text=_("Description of the item or service being paid for."),
	)
	item_number = forms.CharField(
		max_length=127,
		required=False,
		label=_("Item Number"),
		help_text=_("Optional item or order number."),
	)
	custom = forms.CharField(
		max_length=255,
		required=False,
		label=_("Custom Data"),
		help_text=_("Optional custom data for the transaction."),
	)

	def clean_amount(self):
		amount = self.cleaned_data.get("amount")
		if amount <= 0:
			raise forms.ValidationError(_("Amount must be greater than zero."))
		return amount
