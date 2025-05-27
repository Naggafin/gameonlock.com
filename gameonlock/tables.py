import django_tables2 as tables
from .models import Play, Transaction  # Ensure these models are defined in models.py

class BetHistoryTable(tables.Table):
    event = tables.Column()
    bet_slip = tables.Column()
    date_time = tables.DateTimeColumn()
    bet_type = tables.Column()
    bet_amount = tables.Column()
    bet_odd = tables.Column()
    status = tables.Column()
    class Meta:
        model = Play
        template_name = 'django_tables2/semantic.html'
        fields = ['event', 'bet_slip', 'date_time', 'bet_type', 'bet_amount', 'bet_odd', 'status']
        orderable = True

class TransactionHistoryTable(tables.Table):
    transaction_id = tables.Column()
    date_time = tables.DateTimeColumn()
    type = tables.Column()
    amount = tables.Column()
    status = tables.Column()
    class Meta:
        model = Transaction
        template_name = 'django_tables2/semantic.html'
        fields = ['transaction_id', 'date_time', 'type', 'amount', 'status']
        orderable = True
