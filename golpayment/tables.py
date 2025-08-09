import django_tables2 as tables
from django.templatetags.l10n import localize
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Transaction


class TransactionTable(tables.Table):
	type = tables.Column(
		attrs={"th": {"class": "text-start"}, "td": {"class": "trnx-type"}}
	)
	amount = tables.Column(attrs={"td": {"class": "bet-amount"}})
	method = tables.Column(attrs={"td": {"class": "bet-gateway"}})
	transaction_datetime = tables.DateTimeColumn(attrs={"td": {"class": "date-n-time"}})
	transaction_id = tables.Column(attrs={"td": {"class": "trnx-id"}}, orderable=False)

	def render_type(self, value):
		return format_html(
			"""<span class="icon"><i class="fa-solid fa-arrow-up-long"></i></span>
               <span class="text">{}</span>""",
			value,
		)

	def render_amount(self, value):
		return mark_safe('<span class="text">%s</span>' % value)

	def render_method(self, value):
		return mark_safe('<span class="text">%s</span>' % value)

	def render_transaction_datetime(self, record):
		date = record.transaction_datetime.date()
		time = record.transaction_datetime.time()
		return format_html(
			"""<span class="date">{}</span>
               <span class="time">{}</span>""",
			localize(date),
			localize(time),
		)

	def render_transaction_id(self, value):
		return mark_safe('<span class="trnx-id-number">%s</span>' % value)

	class Meta:
		model = Transaction
		template_name = "peredion/dashboard/tables/transaction-history-table.html"
		empty_text = _("There are no %(verbose_name_plural)s to display.") % {
			"verbose_name_plural": model._meta.verbose_name_plural
		}
		fields = ("type", "amount", "method", "transaction_datetime", "transaction_id")
		sequence = (
			"type",
			"amount",
			"method",
			"transaction_datetime",
			"transaction_id",
		)
		attrs = {
			"class": "single-tournament",
			"tbody": {"class": "all-tournament-match all-bet-history"},
		}
		row_attrs = {
			"id": lambda record: f"{record._meta.model_name}_{record.pk}",
			"class": "single-t-match bet-history",
		}
