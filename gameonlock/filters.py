from django_filters import FilterSet, DateFilter, CharFilter
from .models import Play, Transaction  # Ensure these models are defined in models.py

class BetHistoryFilter(FilterSet):
    date_time = DateFilter(field_name='date_time', lookup_expr='gte', label='From Date')
    status = CharFilter(field_name='status', lookup_expr='icontains')
    class Meta:
        model = Play
        fields = ['date_time', 'status']

class TransactionHistoryFilter(FilterSet):
    date_time = DateFilter(field_name='date_time', lookup_expr='gte', label='From Date')
    type = CharFilter(field_name='type', lookup_expr='icontains')
    status = CharFilter(field_name='status', lookup_expr='icontains')
    class Meta:
        model = Transaction
        fields = ['date_time', 'type', 'status']
