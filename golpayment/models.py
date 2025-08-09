from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from model_utils import Choices


class Transaction(models.Model):
	TX_TYPES = Choices(("d", "deposit", _("Deposit")), ("w", "withdraw", _("Withdraw")))
	TX_METHOD = Choices(
		("pp", "paypal", _("PayPal")),
	)

	transaction_id = models.CharField(
		_("trnx ID"),
		max_length=100,
		unique=True,
		help_text=_("Unique identifier for the transaction"),
	)
	transaction_datetime = models.DateTimeField(
		_("date"), help_text=_("Date and time of the transaction")
	)
	type = models.CharField(
		_("type"), max_length=1, choices=TX_TYPES, help_text=_("Type of transaction")
	)
	amount = MoneyField(
		_("amount"),
		max_digits=10,
		decimal_places=2,
		default_currency="USD",
		help_text=_("Transaction amount"),
	)
	method = models.CharField(
		_("gateway"),
		max_length=2,
		choices=TX_METHOD,
		help_text=_("Method of transaction"),
	)
	user = models.ForeignKey(
		"gameonlock.User",
		on_delete=models.CASCADE,
		related_name="transactions",
		help_text=_("Associated user"),
	)

	def __str__(self):
		return _("Transaction %s") % self.transaction_id
