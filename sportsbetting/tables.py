import django_tables2 as tables
from django.template import Template
from django.templatetags.l10n import localize
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Play

EVENT_COL_TEMPLATE = """
{% load i18n %}
{% if in_play %}
	<span class="in-play-tag">{% trans 'in-play' %}</span>
{% end if %}
<div class="event">
	<div class="part-team">
		<div class="s-team">
			<img src="{{ home.logo.url }}"
				 alt=""
				 class="team-icon"
				 nonce="{{ request.nonce }}">
			<span class="team-name">{{ home }}</span>
		</div>
		<div class="s-team">
			<img src="{{ away.logo.url }}"
				 alt=""
				 class="team-icon"
				 nonce="{{ request.nonce }}">
			<span class="team-name">{{ away }}</span>
		</div>
	</div>
	<span class="event-name">{% if game.league %}{{ game.league }}{% else %}{{ game.governing_body }}{% endif %}</span>
</div>
"""


class BetHistoryTable(tables.Table):
	event = tables.Column(verbose_name=_("Event"), empty_values=(), orderable=False)
	placed_datetime = tables.DateTimeColumn(
		verbose_name=_("Date & Time"), attrs={"td": {"class": "date-n-time"}}
	)
	bet_type = tables.Column(
		verbose_name=_("Bet Type"),
		empty_values=(),
		orderable=False,
		attrs={"td": {"class": "bet-type"}},
	)
	amount = tables.Column(
		verbose_name=_("Bet Amount"), attrs={"td": {"class": "bet-amount"}}
	)
	# odds = tables.Column(verbose_name=_("Odds"), empty_values=(), orderable=False)
	status = tables.Column(verbose_name=_("Status"), attrs={"td": {"class": "status"}})
	expand = tables.TemplateColumn(
		verbose_name="",
		template_code="""
		<button class="btn btn-link expand-toggle" 
				@click="toggleRow" 
				:aria-expanded="expandedRows.includes({{ record.id }})"
				aria-label="{% trans 'Toggle details for bet slip' %} {{ record.id }}">
			<i class="fa-solid fa-chevron-down" 
			   :class="{ 'fa-chevron-up': expandedRows.includes({{ record.id }}) }"></i>
		</button>
		""",
		orderable=False,
	)

	def render_event(self, record):
		in_play = record.picks.filter(
			betting_line__game__start_datetime__lte=timezone.now(),
			betting_line__game__is_finished=False,
		).exists()
		pick = record.picks.first()
		game = pick.betting_line.game
		context = {
			"play": record,
			"pick": pick,
			"game": game,
			"home": game.home_team,
			"away": game.away_team,
			"in_play": in_play,
		}
		return Template(EVENT_COL_TEMPLATE).render(context, self.request)

	def render_placed_datetime(self, record):
		date = record.placed_datetime.date()
		time = record.placed_datetime.time()
		return format_html(
			"""<span class="date">{}</span>
					  		<span class="time">{}</span>""",
			localize(date),
			localize(time),
		)

	def render_bet_type(self, record):
		pick_count = len(record.picks)
		value = _("Parlay") if pick_count > 1 else _("Single bet")
		return mark_safe('<span class="text">%s</span>' % value)

	def render_amount(self, value):
		return mark_safe('<span class="text">%s</span>' % value)

	def render_odds(self, record):
		picks = record.picks.all()
		if not picks:
			return "-"
		# Placeholder: Calculate odds (e.g., from betting_line or external API)
		odds = [pick.betting_line.spread or 1.0 for pick in picks]
		combined_odds = round(float(sum(odds) / len(odds)), 2)  # Example
		return f"{combined_odds:.2f}"

	def render_status(self, record):
		if record.status == Play.STATES.completed:
			return format_html(
				'<span class="{}">{}</span>',
				"win" if record.won else "lost",
				"W" if record.won else "L",
			)
		value = Play.STATES[record.status]
		return mark_safe('<span class="text">%s</span>' % value)

	class Meta:
		model = Play
		template_name = "peredion/dashboard/tables/bet-history-table.html"
		empty_text = _("There are no %(verbose_name_plural)s to display.") % {
			"verbose_name_plural": model._meta.verbose_name_plural
		}
		fields = ("event", "placed_datetime", "bet_type", "amount", "status", "expand")
		attrs = {
			"class": "single-tournament",
			"x-data": "betHistoryTable",
			"thead": {"class": "tournament-title"},
			"tbody": {"class": "all-tournament-match"},
		}
		sequence = (
			"event",
			"placed_datetime",
			"bet_type",
			"amount",
			"status",
			"expand",
		)
		row_attrs = {
			"id": lambda record: f"{record._meta.model_name}_{record.id}",
			"class": "single-t-match",
			"x-show": lambda record: f"expandedRows.includes({record.id})",
			"x-transition": "",
		}
