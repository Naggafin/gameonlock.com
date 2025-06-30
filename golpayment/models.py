from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from model_utils import Choices


class Transaction(models.Model):
	STATES = Choices(("p", "pending", _("Pending")), ("c", "completed", _("Completed")))

	transaction_id = models.CharField(
		max_length=100,
		unique=True,
		help_text=_("Unique identifier for the transaction"),
	)
	transaction_datetime = models.DateTimeField(
		help_text=_("Date and time of the transaction")
	)
	type = models.CharField(max_length=50, help_text=_("Type of transaction"))
	amount = MoneyField(
		max_digits=10,
		decimal_places=2,
		default_currency="USD",
		help_text=_("Transaction amount"),
	)
	status = models.CharField(
		max_length=1, choices=STATES, help_text=_("Status of the transaction")
	)
	user = models.ForeignKey(
		"gameonlock.User",
		on_delete=models.CASCADE,
		related_name="transactions",
		help_text=_("Associated user"),
	)

	def __str__(self):
		return f"Transaction {self.transaction_id}"
