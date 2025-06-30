import django_tables2 as tables

from .models import Play


class PlayTable(tables.Table):
	class Meta:
		model = Play
		fields = ("placed_datetime", "amount", "status", "won")
