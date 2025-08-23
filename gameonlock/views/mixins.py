from decimal import Decimal

from django.db.models import (
	Case,
	Count,
	DecimalField,
	F,
	IntegerField,
	Q,
	Sum,
	When,
)
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from view_breadcrumbs import BaseBreadcrumbMixin

from sportsbetting.models import Play


class GameonlockMixin(BaseBreadcrumbMixin):
	home_label = (
		'<span class="icon"><i class="fa-solid fa-house"></i></span> <span class="text">%s</span>'
		% _("Home")
	)

	@property
	def crumbs(self):
		return []

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["title"] = self.title
		return context


class DashboardContextMixin:
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user_plays = self.request.user.plays

		# Aggregate totals
		totals = user_plays.aggregate(
			total_bets=Count("id"),
			total_pending_bets=Count(
				Case(
					When(status=Play.STATES.pending, then=1),
					output_field=IntegerField(),
				)
			),
			total_wins=Count(Case(When(won=True, then=1), output_field=IntegerField())),
			total_losses=Count(
				Case(
					When(Q(won=False) & Q(status=Play.STATES.completed), then=1),
					output_field=IntegerField(),
				)
			),
			total_deposit=Coalesce(
				Sum(
					"amount", output_field=DecimalField(max_digits=10, decimal_places=2)
				),
				Decimal(0),
			),
			total_payout=Coalesce(
				Sum(
					Case(
						When(won=True, then=F("stakes")),
						output_field=DecimalField(max_digits=10, decimal_places=2),
					),
				),
				Decimal(0),
			),
			total_pending_stakes=Coalesce(
				Sum(
					Case(
						When(status=Play.STATES.pending, then=F("stakes")),
						output_field=DecimalField(max_digits=10, decimal_places=2),
					),
				),
				Decimal(0),
			),
		)

		# Calculate percentages (safely)
		total = totals["total_bets"] or 0
		totals["win_pct"] = round((totals["total_wins"] / total) * 100) if total else 0
		totals["loss_pct"] = (
			round((totals["total_losses"] / total) * 100) if total else 0
		)

		context.update(
			{
				"total_bets": totals["total_bets"],
				"total_pending_bets": totals["total_pending_bets"],
				"total_wins": totals["total_wins"],
				"total_losses": totals["total_losses"],
				"total_payout": totals["total_payout"],
				"total_deposit": totals["total_deposit"],
				"total_pending_stakes": totals["total_pending_stakes"],
				"win_pct": totals["win_pct"],
				"loss_pct": totals["loss_pct"],
			}
		)

		return context
