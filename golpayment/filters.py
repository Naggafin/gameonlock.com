import django_filters

from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
	transaction_datetime = django_filters.DateFromToRangeFilter()

	class Meta:
		model = Transaction
		fields = ["transaction_datetime", "type", "method"]
