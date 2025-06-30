import django_tables2 as tables

from .models import Transaction


class TransactionTable(tables.Table):
	class Meta:
		model = Transaction
		fields = ["transaction_datetime", "transaction_id", "type", "amount", "status"]
		orderable = True
